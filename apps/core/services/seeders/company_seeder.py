from apps.invoicing.models import Company
from .base_seeder import BaseSeeder


class CompanySeeder(BaseSeeder):
    
    def seed(self) -> None:
        self.log_info('Seeding company data...')
        
        if Company.objects.exists():
            self.log_info('Company already exists. Skipping.')
            return
        
        company = Company.objects.create(
            business_name='Westforce Removals Company',
            legal_name='Westforce Removals Company Pty Ltd',
            abn='51234567890',
            acn='123456789',
            gst_registered=True,
            address='Unit 5, 123 Industrial Drive',
            postal_code='6105',
            city='Kewdale',
            state='WA',
            phone='(08) 9350 7890',
            email='info@westforce.com.au',
            website='https://westforce.com.au',
            bank_name='Commonwealth Bank',
            bsb='066-123',
            account_number='12345678',
            invoice_prefix='WF',
            current_number=0
        )
        
        self.log_success(f'Created company: {company.business_name}')
