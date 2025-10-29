from datetime import date, timedelta
from decimal import Decimal
from typing import List, Dict, Any
from apps.accounting.models import Income
from apps.expenses.models import Expense, ExpenseCategory
from .base_seeder import BaseSeeder


class TransactionSeeder(BaseSeeder):
    
    def seed(self) -> None:
        self.seed_incomes()
        self.seed_expenses()
    
    def _get_income_data(self) -> List[Dict[str, Any]]:
        today = date.today()
        return [
            {
                'service_type': 'local',
                'amount': Decimal('650.00'),
                'date': today - timedelta(days=30),
                'payment_method': 'CARD',
                'client_name': 'Sarah Johnson',
                'pickup_address': '25 Murray Street, Perth WA 6000',
                'delivery_address': '48 Beaufort Street, Mount Lawley WA 6050',
                'description': '2-bedroom apartment move with packing',
                'reference_number': 'WF-2024-001'
            },
            {
                'service_type': 'local',
                'amount': Decimal('1450.00'),
                'date': today - timedelta(days=28),
                'payment_method': 'BANK_TRANSFER',
                'client_name': 'Perth Legal Associates',
                'pickup_address': 'Level 3, 89 St Georges Terrace, Perth WA 6000',
                'delivery_address': 'Level 15, 140 St Georges Terrace, Perth WA 6000',
                'description': 'Office relocation - 50 desks and IT equipment',
                'reference_number': 'WF-2024-002'
            },
            {
                'service_type': 'storage',
                'amount': Decimal('220.00'),
                'date': today - timedelta(days=25),
                'payment_method': 'EFTPOS',
                'client_name': 'Michael Chen',
                'pickup_address': '12 Kings Park Road, West Perth WA 6005',
                'delivery_address': 'Storage Unit 45, Kewdale WA 6105',
                'description': 'Storage for 2 months - furniture and boxes',
                'reference_number': 'WF-2024-003'
            },
            {
                'service_type': 'interstate',
                'amount': Decimal('2800.00'),
                'date': today - timedelta(days=20),
                'payment_method': 'BANK_TRANSFER',
                'client_name': 'Emma Thompson',
                'pickup_address': '15 South Terrace, Fremantle WA 6160',
                'delivery_address': '256 Collins Street, Melbourne VIC 3000',
                'description': 'Interstate move Perth to Melbourne - 3-bedroom house',
                'reference_number': 'WF-2024-004'
            },
            {
                'service_type': 'packing',
                'amount': Decimal('380.00'),
                'date': today - timedelta(days=15),
                'payment_method': 'CARD',
                'client_name': 'Robert Wilson',
                'pickup_address': '78 Rokeby Road, Subiaco WA 6008',
                'delivery_address': '78 Rokeby Road, Subiaco WA 6008',
                'description': 'Professional packing - fragile items and artwork',
                'reference_number': 'WF-2024-005'
            },
            {
                'service_type': 'cleaning',
                'amount': Decimal('320.00'),
                'date': today - timedelta(days=12),
                'payment_method': 'EFTPOS',
                'client_name': 'Lisa Martinez',
                'pickup_address': '32 Hampton Road, Fremantle WA 6160',
                'delivery_address': '32 Hampton Road, Fremantle WA 6160',
                'description': 'End of lease cleaning - 2-bedroom apartment',
                'reference_number': 'WF-2024-006'
            },
            {
                'service_type': 'local',
                'amount': Decimal('890.00'),
                'date': today - timedelta(days=8),
                'payment_method': 'BANK_TRANSFER',
                'client_name': 'James Anderson',
                'pickup_address': '155 Adelaide Terrace, East Perth WA 6004',
                'delivery_address': '29 Labouchere Road, South Perth WA 6151',
                'description': '3-bedroom house move with piano transport',
                'reference_number': 'WF-2024-007'
            },
            {
                'service_type': 'local',
                'amount': Decimal('520.00'),
                'date': today - timedelta(days=5),
                'payment_method': 'CARD',
                'client_name': 'David Kumar',
                'pickup_address': '67 Stirling Highway, Nedlands WA 6009',
                'delivery_address': '89 Railway Parade, West Leederville WA 6007',
                'description': '1-bedroom apartment move',
                'reference_number': 'WF-2024-008'
            },
            {
                'service_type': 'local',
                'amount': Decimal('1100.00'),
                'date': today - timedelta(days=3),
                'payment_method': 'BANK_TRANSFER',
                'client_name': 'Tech Startup Ltd',
                'pickup_address': 'Level 2, 250 St Georges Terrace, Perth WA 6000',
                'delivery_address': 'Suite 10, 45 Kings Park Road, West Perth WA 6005',
                'description': 'Small office relocation',
                'reference_number': 'WF-2024-009'
            },
            {
                'service_type': 'local',
                'amount': Decimal('750.00'),
                'date': today - timedelta(days=1),
                'payment_method': 'EFTPOS',
                'client_name': 'Sophie Williams',
                'pickup_address': '156 Stirling Street, Perth WA 6000',
                'delivery_address': '78 The Esplanade, Scarborough WA 6019',
                'description': '2-bedroom unit move',
                'reference_number': 'WF-2024-010'
            },
        ]
    
    def _get_expense_data(self, categories: Dict) -> List[Dict[str, Any]]:
        today = date.today()
        return [
            {
                'category': categories.get('office-rent'),
                'amount': Decimal('2200.00'),
                'date': today.replace(day=1),
                'description': 'Monthly rent for office and warehouse - Kewdale',
                'invoice_number': 'RENT-2024-10'
            },
            {
                'category': categories.get('electricity'),
                'amount': Decimal('385.50'),
                'date': today - timedelta(days=25),
                'description': 'Electricity bill - office and warehouse',
                'invoice_number': 'PWR-2024-001'
            },
            {
                'category': categories.get('water-utilities'),
                'amount': Decimal('145.80'),
                'date': today - timedelta(days=23),
                'description': 'Water and utilities',
                'invoice_number': 'WAT-2024-001'
            },
            {
                'category': categories.get('internet-phone'),
                'amount': Decimal('189.00'),
                'date': today - timedelta(days=20),
                'description': 'Business internet and phone services',
                'invoice_number': 'TEL-2024-001'
            },
            {
                'category': categories.get('insurance'),
                'amount': Decimal('1650.00'),
                'date': today - timedelta(days=60),
                'description': 'Quarterly public liability and vehicle insurance',
                'invoice_number': 'INS-2024-Q3'
            },
            {
                'category': categories.get('vehicle-registration'),
                'amount': Decimal('890.00'),
                'date': today - timedelta(days=90),
                'description': 'Annual registration - truck WA-1234',
                'invoice_number': 'REGO-2024-001'
            },
            {
                'category': categories.get('fuel'),
                'amount': Decimal('580.75'),
                'date': today - timedelta(days=15),
                'description': 'Diesel for trucks - October',
                'invoice_number': 'FUEL-2024-10-01'
            },
            {
                'category': categories.get('fuel'),
                'amount': Decimal('620.30'),
                'date': today - timedelta(days=8),
                'description': 'Diesel for trucks - October',
                'invoice_number': 'FUEL-2024-10-02'
            },
            {
                'category': categories.get('vehicle-maintenance'),
                'amount': Decimal('850.00'),
                'date': today - timedelta(days=18),
                'description': 'Truck service and oil change - WA-1234',
                'invoice_number': 'MAINT-2024-001'
            },
            {
                'category': categories.get('packing-materials'),
                'amount': Decimal('320.50'),
                'date': today - timedelta(days=12),
                'description': 'Boxes, bubble wrap, and tape supplies',
                'invoice_number': 'PACK-2024-001'
            },
            {
                'category': categories.get('staff-wages'),
                'amount': Decimal('3200.00'),
                'date': today - timedelta(days=14),
                'description': 'Casual staff wages - fortnight ending',
                'invoice_number': 'WAGES-2024-20'
            },
            {
                'category': categories.get('marketing'),
                'amount': Decimal('450.00'),
                'date': today - timedelta(days=10),
                'description': 'Google Ads campaign - October',
                'invoice_number': 'ADS-2024-10'
            },
            {
                'category': categories.get('gst-payable'),
                'amount': Decimal('1850.00'),
                'date': today.replace(day=28) - timedelta(days=90),
                'description': 'BAS - Q3 2024 GST payment',
                'invoice_number': 'BAS-2024-Q3'
            },
            {
                'category': categories.get('superannuation'),
                'amount': Decimal('480.00'),
                'date': today - timedelta(days=7),
                'description': 'Super contributions for employees',
                'invoice_number': 'SUPER-2024-10'
            },
            {
                'category': categories.get('equipment-purchase'),
                'amount': Decimal('680.00'),
                'date': today - timedelta(days=45),
                'description': 'New furniture dollies and straps',
                'invoice_number': 'EQUIP-2024-001'
            },
            {
                'category': categories.get('professional-services'),
                'amount': Decimal('550.00'),
                'date': today - timedelta(days=30),
                'description': 'Accountant fees - quarterly bookkeeping',
                'invoice_number': 'ACCT-2024-Q3'
            },
        ]
    
    def seed_incomes(self) -> None:
        self.log_info('Seeding income transactions...')
        
        if Income.objects.exists():
            self.log_info('Income records already exist. Skipping.')
            return
        
        created_count = 0
        for income_data in self._get_income_data():
            Income.objects.create(**income_data)
            created_count += 1
        
        self.log_success(f'Created {created_count} income records')
    
    def seed_expenses(self) -> None:
        self.log_info('Seeding expense transactions...')
        
        if Expense.objects.exists():
            self.log_info('Expense records already exist. Skipping.')
            return
        
        categories = {cat.slug: cat for cat in ExpenseCategory.objects.all()}
        
        if not categories:
            self.log_error('No expense categories found. Run category seeder first.')
            return
        
        created_count = 0
        for expense_data in self._get_expense_data(categories):
            if expense_data['category']:
                Expense.objects.create(**expense_data)
                created_count += 1
        
        self.log_success(f'Created {created_count} expense records')
