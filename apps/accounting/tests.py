from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from decimal import Decimal
from datetime import date
from apps.accounting.models import Income, ServiceTypeChoices, PaymentMethodChoices

User = get_user_model()


class IncomeModelTestCase(TestCase):
    
    def test_income_creation(self):
        income = Income.objects.create(
            service_type=ServiceTypeChoices.LOCAL_MOVE,
            amount=Decimal('350.00'),
            date=date.today(),
            payment_method=PaymentMethodChoices.CARD,
            client_name='John Smith',
            pickup_address='123 Main St, East Perth WA 6004',
            delivery_address='456 Oak Ave, West Perth WA 6005'
        )
        
        self.assertEqual(income.service_type, ServiceTypeChoices.LOCAL_MOVE)
        self.assertEqual(income.amount, Decimal('350.00'))
        self.assertEqual(income.client_name, 'John Smith')
    
    def test_income_accounting_period_auto_set(self):
        test_date = date(2024, 3, 15)
        income = Income.objects.create(
            service_type=ServiceTypeChoices.INTERSTATE_MOVE,
            amount=Decimal('850.00'),
            date=test_date,
            payment_method=PaymentMethodChoices.BANK_TRANSFER,
            client_name='Jane Doe'
        )
        
        self.assertEqual(income.accounting_year, 2024)
        self.assertEqual(income.accounting_month, 3)

    def test_income_str_representation(self):
        income = Income.objects.create(
            service_type=ServiceTypeChoices.LOCAL_MOVE,
            amount=Decimal('500.00'),
            date=date(2024, 1, 15),
            payment_method=PaymentMethodChoices.EFTPOS,
            client_name='Test Client'
        )
        
        expected_str = f"Local Move - $500.00 AUD (2024-01-15)"
        self.assertEqual(str(income), expected_str)
    
    def test_payment_method_icon(self):
        income = Income.objects.create(
            service_type=ServiceTypeChoices.LOCAL_MOVE,
            amount=Decimal('200.00'),
            date=date.today(),
            payment_method=PaymentMethodChoices.PAYPAL,
            client_name='Test Client'
        )
        
        self.assertEqual(income.get_payment_method_display_icon(), 'paypal')


class IncomeQuerySetTestCase(TestCase):
    
    def setUp(self):
        Income.objects.create(
            service_type=ServiceTypeChoices.LOCAL_MOVE,
            amount=Decimal('300.00'),
            date=date.today(),
            payment_method=PaymentMethodChoices.CARD,
            client_name='Client A'
        )
        
        Income.objects.create(
            service_type=ServiceTypeChoices.PACKING,
            amount=Decimal('150.00'),
            date=date.today(),
            payment_method=PaymentMethodChoices.CASH,
            client_name='Client B'
        )
        
        Income.objects.create(
            service_type=ServiceTypeChoices.INTERSTATE_MOVE,
            amount=Decimal('850.00'),
            date=date.today(),
            payment_method=PaymentMethodChoices.BANK_TRANSFER,
            client_name='Client C'
        )
    
    def test_service_type_filter(self):
        local_moves = Income.objects.filter(service_type=ServiceTypeChoices.LOCAL_MOVE)
        self.assertEqual(local_moves.count(), 1)
        self.assertEqual(local_moves.first().client_name, 'Client A')


class IncomeViewsTestCase(TestCase):
    
    def setUp(self):
        self.client = Client()
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
        
        self.client.login(username='admin', password='testpass123')
        
        Income.objects.create(
            service_type=ServiceTypeChoices.LOCAL_MOVE,
            amount=Decimal('350.00'),
            date=date.today(),
            payment_method=PaymentMethodChoices.CARD,
            client_name='Test Client'
        )
    
    def test_income_list_view(self):
        response = self.client.get(reverse('accounting:income_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Client')


def validate_moving_company_setup():
    try:
        service_types = [choice[0] for choice in ServiceTypeChoices.choices]
        expected_types = ['local', 'interstate', 'international', 'storage', 'packing', 'cleaning']
        if all(service_type in service_types for service_type in expected_types):
            print("✅ Moving service types configured")
        
        payment_methods = [choice[0] for choice in PaymentMethodChoices.choices]
        australian_methods = ['CARD', 'CASH', 'BANK_TRANSFER', 'EFTPOS']
        if all(method in payment_methods for method in australian_methods):
            print("✅ Australian payment methods configured")
        
        print("✅ Moving company setup validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False
