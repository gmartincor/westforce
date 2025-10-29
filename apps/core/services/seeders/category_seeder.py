from typing import List, Dict, Any
from apps.expenses.models import ExpenseCategory
from .base_seeder import BaseSeeder


class CategorySeeder(BaseSeeder):
    
    CATEGORIES = [
        {'name': 'Office Rent', 'slug': 'office-rent', 'category_type': 'FIXED', 
         'description': 'Monthly rental costs for office and storage facilities'},
        {'name': 'Electricity', 'slug': 'electricity', 'category_type': 'FIXED',
         'description': 'Power bills for office and storage facilities'},
        {'name': 'Water & Utilities', 'slug': 'water-utilities', 'category_type': 'FIXED',
         'description': 'Water, gas and other utility bills'},
        {'name': 'Internet & Phone', 'slug': 'internet-phone', 'category_type': 'FIXED',
         'description': 'Telecommunications and internet services'},
        {'name': 'Insurance', 'slug': 'insurance', 'category_type': 'FIXED',
         'description': 'Public liability, vehicle and equipment insurance'},
        {'name': 'Vehicle Registration', 'slug': 'vehicle-registration', 'category_type': 'FIXED',
         'description': 'Annual vehicle registration fees'},
        {'name': 'Fuel', 'slug': 'fuel', 'category_type': 'VARIABLE',
         'description': 'Petrol and diesel for moving trucks'},
        {'name': 'Vehicle Maintenance', 'slug': 'vehicle-maintenance', 'category_type': 'VARIABLE',
         'description': 'Truck servicing, repairs and maintenance'},
        {'name': 'Packing Materials', 'slug': 'packing-materials', 'category_type': 'VARIABLE',
         'description': 'Boxes, bubble wrap, tape and packing supplies'},
        {'name': 'Staff Wages', 'slug': 'staff-wages', 'category_type': 'VARIABLE',
         'description': 'Employee wages and casual staff payments'},
        {'name': 'Marketing', 'slug': 'marketing', 'category_type': 'VARIABLE',
         'description': 'Online advertising and promotional materials'},
        {'name': 'GST Payable', 'slug': 'gst-payable', 'category_type': 'TAX',
         'description': 'Goods and Services Tax payments to ATO'},
        {'name': 'PAYG Tax', 'slug': 'payg-tax', 'category_type': 'TAX',
         'description': 'Pay As You Go income tax instalments'},
        {'name': 'Superannuation', 'slug': 'superannuation', 'category_type': 'TAX',
         'description': 'Compulsory super contributions for employees'},
        {'name': 'Equipment Purchase', 'slug': 'equipment-purchase', 'category_type': 'OCCASIONAL',
         'description': 'Dollies, straps, protective equipment and tools'},
        {'name': 'Professional Services', 'slug': 'professional-services', 'category_type': 'OCCASIONAL',
         'description': 'Accountant, legal and business advisory fees'},
        {'name': 'Licenses & Permits', 'slug': 'licenses-permits', 'category_type': 'OCCASIONAL',
         'description': 'Business licenses and operating permits'},
    ]
    
    def seed(self) -> None:
        self.log_info('Seeding expense categories...')
        
        created_count = 0
        for category_data in self.CATEGORIES:
            _, created = self.get_or_skip(
                ExpenseCategory,
                slug=category_data['slug'],
                defaults=category_data
            )
            if created:
                created_count += 1
        
        self.log_success(f'Created {created_count} expense categories')
