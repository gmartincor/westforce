from datetime import date, timedelta
from decimal import Decimal
from typing import List, Dict, Any
import random
from apps.accounting.models import Income
from apps.expenses.models import Expense, ExpenseCategory
from .base_seeder import BaseSeeder


class YearlyTransactionSeeder(BaseSeeder):
    
    INCOME_TEMPLATES = [
        {
            'service_type': 'local',
            'payment_method': 'CARD',
            'client_name': 'Sarah Johnson',
            'pickup_address': '25 Murray Street, Perth WA 6000',
            'delivery_address': '48 Beaufort Street, Mount Lawley WA 6050',
            'description': '2-bedroom apartment move with packing',
            'amount_range': (550, 750)
        },
        {
            'service_type': 'local',
            'payment_method': 'BANK_TRANSFER',
            'client_name': 'Perth Legal Associates',
            'pickup_address': 'Level 3, 89 St Georges Terrace, Perth WA 6000',
            'delivery_address': 'Level 15, 140 St Georges Terrace, Perth WA 6000',
            'description': 'Office relocation',
            'amount_range': (1200, 1800)
        },
        {
            'service_type': 'storage',
            'payment_method': 'EFTPOS',
            'client_name': 'Michael Chen',
            'pickup_address': '12 Kings Park Road, West Perth WA 6005',
            'delivery_address': 'Storage Unit 45, Kewdale WA 6105',
            'description': 'Storage service',
            'amount_range': (180, 280)
        },
        {
            'service_type': 'interstate',
            'payment_method': 'BANK_TRANSFER',
            'client_name': 'Emma Thompson',
            'pickup_address': '15 South Terrace, Fremantle WA 6160',
            'delivery_address': '256 Collins Street, Melbourne VIC 3000',
            'description': 'Interstate move Perth to Melbourne',
            'amount_range': (2500, 3200)
        },
        {
            'service_type': 'packing',
            'payment_method': 'CARD',
            'client_name': 'Robert Wilson',
            'pickup_address': '78 Rokeby Road, Subiaco WA 6008',
            'delivery_address': '78 Rokeby Road, Subiaco WA 6008',
            'description': 'Professional packing service',
            'amount_range': (300, 450)
        },
        {
            'service_type': 'cleaning',
            'payment_method': 'EFTPOS',
            'client_name': 'Lisa Martinez',
            'pickup_address': '32 Hampton Road, Fremantle WA 6160',
            'delivery_address': '32 Hampton Road, Fremantle WA 6160',
            'description': 'End of lease cleaning',
            'amount_range': (280, 380)
        },
        {
            'service_type': 'local',
            'payment_method': 'BANK_TRANSFER',
            'client_name': 'James Anderson',
            'pickup_address': '155 Adelaide Terrace, East Perth WA 6004',
            'delivery_address': '29 Labouchere Road, South Perth WA 6151',
            'description': '3-bedroom house move',
            'amount_range': (800, 1100)
        },
        {
            'service_type': 'local',
            'payment_method': 'CARD',
            'client_name': 'David Kumar',
            'pickup_address': '67 Stirling Highway, Nedlands WA 6009',
            'delivery_address': '89 Railway Parade, West Leederville WA 6007',
            'description': '1-bedroom apartment move',
            'amount_range': (450, 600)
        },
    ]
    
    EXPENSE_TEMPLATES = {
        'monthly': [
            {
                'slug': 'office-rent',
                'amount': Decimal('2200.00'),
                'description': 'Monthly rent for office and warehouse - Kewdale',
                'invoice_prefix': 'RENT',
                'day': 1
            },
            {
                'slug': 'electricity',
                'amount_range': (350, 450),
                'description': 'Electricity bill - office and warehouse',
                'invoice_prefix': 'PWR',
                'day': 3
            },
            {
                'slug': 'water-utilities',
                'amount_range': (120, 180),
                'description': 'Water and utilities',
                'invoice_prefix': 'WAT',
                'day': 5
            },
            {
                'slug': 'internet-phone',
                'amount': Decimal('189.00'),
                'description': 'Business internet and phone services',
                'invoice_prefix': 'TEL',
                'day': 8
            },
            {
                'slug': 'fuel',
                'amount_range': (500, 700),
                'description': 'Diesel for trucks',
                'invoice_prefix': 'FUEL',
                'day': 13,
                'count': 2
            },
            {
                'slug': 'packing-materials',
                'amount_range': (250, 400),
                'description': 'Boxes, bubble wrap, and tape supplies',
                'invoice_prefix': 'PACK',
                'day': 16
            },
            {
                'slug': 'staff-wages',
                'amount_range': (2800, 3600),
                'description': 'Casual staff wages - fortnight ending',
                'invoice_prefix': 'WAGES',
                'day': 14
            },
            {
                'slug': 'marketing',
                'amount_range': (350, 550),
                'description': 'Google Ads campaign',
                'invoice_prefix': 'ADS',
                'day': 18
            },
            {
                'slug': 'superannuation',
                'amount_range': (400, 550),
                'description': 'Super contributions for employees',
                'invoice_prefix': 'SUPER',
                'day': 21
            },
        ],
        'quarterly': [
            {
                'slug': 'insurance',
                'amount': Decimal('1650.00'),
                'description': 'Quarterly public liability and vehicle insurance',
                'invoice_prefix': 'INS',
                'day': 2,
                'months': [1, 4, 7, 10]
            },
            {
                'slug': 'gst-payable',
                'amount_range': (1600, 2200),
                'description': 'BAS GST payment',
                'invoice_prefix': 'BAS',
                'day': 28,
                'months': [1, 4, 7, 10]
            },
            {
                'slug': 'professional-services',
                'amount': Decimal('550.00'),
                'description': 'Accountant fees - quarterly bookkeeping',
                'invoice_prefix': 'ACCT',
                'day': 25,
                'months': [3, 6, 9, 12]
            },
        ],
        'occasional': [
            {
                'slug': 'vehicle-registration',
                'amount': Decimal('890.00'),
                'description': 'Annual registration - truck WA-1234',
                'invoice_prefix': 'REGO',
                'day': 15,
                'months': [1, 7]
            },
            {
                'slug': 'vehicle-maintenance',
                'amount_range': (700, 1000),
                'description': 'Truck service and oil change',
                'invoice_prefix': 'MAINT',
                'day': 10,
                'frequency': 0.4
            },
            {
                'slug': 'equipment-purchase',
                'amount_range': (400, 900),
                'description': 'Equipment and tools',
                'invoice_prefix': 'EQUIP',
                'day': 12,
                'frequency': 0.25
            },
        ]
    }
    
    def seed(self) -> None:
        self.seed_yearly_incomes()
        self.seed_yearly_expenses()
    
    def _generate_amount(self, config: Dict) -> Decimal:
        if 'amount' in config:
            return config['amount']
        min_amt, max_amt = config['amount_range']
        return Decimal(str(random.randint(int(min_amt), int(max_amt))))
    
    def _generate_incomes_for_month(self, year: int, month: int) -> List[Dict[str, Any]]:
        incomes = []
        month_start = date(year, month, 1)
        
        num_transactions = random.randint(8, 15)
        counter = 1
        
        for i in range(num_transactions):
            template = random.choice(self.INCOME_TEMPLATES)
            day = random.randint(1, 28)
            
            income = {
                'service_type': template['service_type'],
                'amount': self._generate_amount(template),
                'date': month_start.replace(day=day),
                'payment_method': template['payment_method'],
                'client_name': template['client_name'],
                'pickup_address': template['pickup_address'],
                'delivery_address': template['delivery_address'],
                'description': template['description'],
                'reference_number': f'WF-{year}-{month:02d}-{counter:03d}'
            }
            incomes.append(income)
            counter += 1
        
        return incomes
    
    def _generate_expenses_for_month(self, year: int, month: int, categories: Dict) -> List[Dict[str, Any]]:
        expenses = []
        month_start = date(year, month, 1)
        
        for expense_config in self.EXPENSE_TEMPLATES['monthly']:
            count = expense_config.get('count', 1)
            for i in range(count):
                category = categories.get(expense_config['slug'])
                if not category:
                    continue
                
                day = expense_config['day'] + (i * 7 if count > 1 else 0)
                if day > 28:
                    day = 28
                
                expense = {
                    'category': category,
                    'amount': self._generate_amount(expense_config),
                    'date': month_start.replace(day=day),
                    'description': expense_config['description'],
                    'invoice_number': f"{expense_config['invoice_prefix']}-{year}-{month:02d}" + (f"-{i+1:02d}" if count > 1 else '')
                }
                expenses.append(expense)
        
        for expense_config in self.EXPENSE_TEMPLATES['quarterly']:
            if month in expense_config['months']:
                category = categories.get(expense_config['slug'])
                if not category:
                    continue
                
                quarter = (month - 1) // 3 + 1
                expense = {
                    'category': category,
                    'amount': self._generate_amount(expense_config),
                    'date': month_start.replace(day=expense_config['day']),
                    'description': f"{expense_config['description']} - Q{quarter}",
                    'invoice_number': f"{expense_config['invoice_prefix']}-{year}-Q{quarter}"
                }
                expenses.append(expense)
        
        for expense_config in self.EXPENSE_TEMPLATES['occasional']:
            should_create = False
            
            if 'months' in expense_config:
                should_create = month in expense_config['months']
            elif 'frequency' in expense_config:
                should_create = random.random() < expense_config['frequency']
            
            if should_create:
                category = categories.get(expense_config['slug'])
                if not category:
                    continue
                
                expense = {
                    'category': category,
                    'amount': self._generate_amount(expense_config),
                    'date': month_start.replace(day=expense_config['day']),
                    'description': expense_config['description'],
                    'invoice_number': f"{expense_config['invoice_prefix']}-{year}-{month:02d}"
                }
                expenses.append(expense)
        
        return expenses
    
    def seed_yearly_incomes(self) -> None:
        self.log_info('Seeding yearly income transactions...')
        
        if Income.objects.exists():
            self.log_info('Deleting existing income records...')
            Income.objects.all().delete()
        
        year = 2025
        total_created = 0
        
        for month in range(1, 13):
            incomes = self._generate_incomes_for_month(year, month)
            for income_data in incomes:
                Income.objects.create(**income_data)
                total_created += 1
        
        self.log_success(f'Created {total_created} income records across 12 months')
    
    def seed_yearly_expenses(self) -> None:
        self.log_info('Seeding yearly expense transactions...')
        
        if Expense.objects.exists():
            self.log_info('Deleting existing expense records...')
            Expense.objects.all().delete()
        
        categories = {cat.slug: cat for cat in ExpenseCategory.objects.all()}
        
        if not categories:
            self.log_error('No expense categories found. Run category seeder first.')
            return
        
        year = 2025
        total_created = 0
        
        for month in range(1, 13):
            expenses = self._generate_expenses_for_month(year, month, categories)
            for expense_data in expenses:
                Expense.objects.create(**expense_data)
                total_created += 1
        
        self.log_success(f'Created {total_created} expense records across 12 months')
