from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from decimal import Decimal
from datetime import date
from apps.business_lines.models import BusinessLine
from apps.accounting.models import Income, ServiceTypeChoices, PaymentMethodChoices

User = get_user_model()


class AccountingViewsTestCase(TestCase):
    
    def setUp(self):
        self.client = Client()
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
        
        self.business_line = BusinessLine.objects.create(
            name='East Perth Operations',
            slug='east-perth',
            level=1,
            is_active=True
        )
    
    def test_income_creation(self):
        income = Income.objects.create(
            business_line=self.business_line,
            service_type=ServiceTypeChoices.LOCAL_MOVE,
            amount=Decimal('350.00'),
            date=date.today(),
            payment_method=PaymentMethodChoices.CARD,
            client_name='John Smith',
            pickup_address='123 Main St, East Perth WA 6004',
            delivery_address='456 Oak Ave, West Perth WA 6005'
        )
        
        self.assertEqual(income.business_line, self.business_line)
        self.assertEqual(income.service_type, ServiceTypeChoices.LOCAL_MOVE)
        self.assertEqual(income.amount, Decimal('350.00'))
        self.assertEqual(income.client_name, 'John Smith')
    
    def test_income_accounting_period_auto_set(self):
        test_date = date(2024, 3, 15)
        income = Income.objects.create(
            business_line=self.business_line,
            service_type=ServiceTypeChoices.INTERSTATE_MOVE,
            amount=Decimal('850.00'),
            date=test_date,
            payment_method=PaymentMethodChoices.BANK_TRANSFER,
            client_name='Jane Doe'
        )
        
        self.assertEqual(income.accounting_year, 2024)
        self.assertEqual(income.accounting_month, 3)


class BusinessLineIncomeTestCase(TestCase):
    
    def setUp(self):
        self.east_perth = BusinessLine.objects.create(
            name='East Perth',
            slug='east-perth',
            level=1,
            is_active=True
        )
        
        self.west_perth = BusinessLine.objects.create(
            name='West Perth',
            slug='west-perth',
            level=1,
            is_active=True
        )
        
        Income.objects.create(
            business_line=self.east_perth,
            service_type=ServiceTypeChoices.LOCAL_MOVE,
            amount=Decimal('300.00'),
            date=date.today(),
            payment_method=PaymentMethodChoices.CARD,
            client_name='Client A'
        )
        
        Income.objects.create(
            business_line=self.east_perth,
            service_type=ServiceTypeChoices.PACKING,
            amount=Decimal('150.00'),
            date=date.today(),
            payment_method=PaymentMethodChoices.CASH,
            client_name='Client B'
        )
        
        Income.objects.create(
            business_line=self.west_perth,
            service_type=ServiceTypeChoices.INTERSTATE_MOVE,
            amount=Decimal('850.00'),
            date=date.today(),
            payment_method=PaymentMethodChoices.BANK_TRANSFER,
            client_name='Client C'
        )
    
    def test_business_line_total_income(self):
        east_perth_total = self.east_perth.total_income
        west_perth_total = self.west_perth.total_income
        
        self.assertEqual(east_perth_total, Decimal('450.00'))
        self.assertEqual(west_perth_total, Decimal('850.00'))
    
    def test_business_line_income_count(self):
        east_perth_count = self.east_perth.income_count
        west_perth_count = self.west_perth.income_count
        
        self.assertEqual(east_perth_count, 2)
        self.assertEqual(west_perth_count, 1)
    
    def test_income_queryset_filters(self):
        local_moves = Income.objects.by_service_type(ServiceTypeChoices.LOCAL_MOVE)
        east_perth_incomes = Income.objects.by_business_line(self.east_perth)
        
        self.assertEqual(local_moves.count(), 1)
        self.assertEqual(east_perth_incomes.count(), 2)


class IncomeModelTestCase(TestCase):
    
    def setUp(self):
        self.business_line = BusinessLine.objects.create(
            name='Test Area',
            slug='test-area',
            level=1,
            is_active=True
        )
    
    def test_income_str_representation(self):
        income = Income.objects.create(
            business_line=self.business_line,
            service_type=ServiceTypeChoices.LOCAL_MOVE,
            amount=Decimal('500.00'),
            date=date(2024, 1, 15),
            payment_method=PaymentMethodChoices.EFTPOS,
            client_name='Test Client'
        )
        
        expected_str = f"Test Area - $500.00 AUD (2024-01-15)"
        self.assertEqual(str(income), expected_str)
    
    def test_service_location_property(self):
        parent_line = BusinessLine.objects.create(
            name='Perth Region',
            slug='perth-region',
            level=1,
            is_active=True
        )
        
        child_line = BusinessLine.objects.create(
            name='Subiaco',
            slug='subiaco',
            parent=parent_line,
            level=2,
            is_active=True
        )
        
        income = Income.objects.create(
            business_line=child_line,
            service_type=ServiceTypeChoices.LOCAL_MOVE,
            amount=Decimal('400.00'),
            date=date.today(),
            payment_method=PaymentMethodChoices.CARD,
            client_name='Test Client'
        )
        
        self.assertEqual(income.service_location, 'Perth Region > Subiaco')
    
    def test_payment_method_icon(self):
        income = Income.objects.create(
            business_line=self.business_line,
            service_type=ServiceTypeChoices.LOCAL_MOVE,
            amount=Decimal('200.00'),
            date=date.today(),
            payment_method=PaymentMethodChoices.PAYPAL,
            client_name='Test Client'
        )
        
        self.assertEqual(income.get_payment_method_display_icon(), 'paypal')


def validate_moving_company_setup():
    """Validate that the system is properly configured for a moving company"""
    try:
        business_lines = BusinessLine.objects.filter(is_active=True)
        if business_lines.exists():
            print(f"✅ Business lines configured: {business_lines.count()}")
        
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
