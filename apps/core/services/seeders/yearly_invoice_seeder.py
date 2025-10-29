from datetime import date, timedelta
from decimal import Decimal
from typing import List, Dict, Any
import random
from apps.invoicing.models import Company, Invoice, InvoiceItem
from .base_seeder import BaseSeeder


class YearlyInvoiceSeeder(BaseSeeder):
    
    INVOICE_TEMPLATES = [
        {
            'client_type': 'INDIVIDUAL',
            'client_name': 'Sarah Johnson',
            'client_abn': '',
            'client_address': '25 Murray Street, Perth WA 6000',
            'payment_terms': 'Payment due within 14 days',
            'items': [
                {
                    'description': '2-bedroom apartment move - labour and truck hire',
                    'quantity': 1,
                    'unit_price_range': (550, 700),
                    'gst_treatment': 'TAXABLE'
                }
            ]
        },
        {
            'client_type': 'BUSINESS',
            'client_name': 'Perth Legal Associates Pty Ltd',
            'client_abn': '51987654321',
            'client_address': 'Level 3, 89 St Georges Terrace, Perth WA 6000',
            'payment_terms': 'Payment due within 30 days',
            'items': [
                {
                    'description': 'Office relocation services',
                    'quantity': 1,
                    'unit_price_range': (1200, 1800),
                    'gst_treatment': 'TAXABLE'
                }
            ]
        },
        {
            'client_type': 'INDIVIDUAL',
            'client_name': 'Michael Chen',
            'client_abn': '',
            'client_address': '12 Kings Park Road, West Perth WA 6005',
            'payment_terms': 'Payment due within 14 days',
            'items': [
                {
                    'description': 'Storage rental services',
                    'quantity': 1,
                    'unit_price_range': (180, 250),
                    'gst_treatment': 'TAXABLE'
                }
            ]
        },
        {
            'client_type': 'INDIVIDUAL',
            'client_name': 'Emma Thompson',
            'client_abn': '',
            'client_address': '15 South Terrace, Fremantle WA 6160',
            'payment_terms': 'Payment due within 7 days',
            'items': [
                {
                    'description': 'Interstate move - 3-bedroom house',
                    'quantity': 1,
                    'unit_price_range': (2500, 3200),
                    'gst_treatment': 'TAXABLE'
                }
            ]
        },
        {
            'client_type': 'INDIVIDUAL',
            'client_name': 'Robert Wilson',
            'client_abn': '',
            'client_address': '78 Rokeby Road, Subiaco WA 6008',
            'payment_terms': 'Payment due within 14 days',
            'items': [
                {
                    'description': 'Professional packing service',
                    'quantity': 1,
                    'unit_price_range': (300, 450),
                    'gst_treatment': 'TAXABLE'
                }
            ]
        },
        {
            'client_type': 'INDIVIDUAL',
            'client_name': 'Lisa Martinez',
            'client_abn': '',
            'client_address': '32 Hampton Road, Fremantle WA 6160',
            'payment_terms': 'Payment due within 14 days',
            'items': [
                {
                    'description': 'End of lease cleaning',
                    'quantity': 1,
                    'unit_price_range': (280, 380),
                    'gst_treatment': 'TAXABLE'
                }
            ]
        },
        {
            'client_type': 'INDIVIDUAL',
            'client_name': 'James Anderson',
            'client_abn': '',
            'client_address': '155 Adelaide Terrace, East Perth WA 6004',
            'payment_terms': 'Payment due within 14 days',
            'items': [
                {
                    'description': '3-bedroom house move with piano',
                    'quantity': 1,
                    'unit_price_range': (850, 1150),
                    'gst_treatment': 'TAXABLE'
                }
            ]
        },
        {
            'client_type': 'INDIVIDUAL',
            'client_name': 'David Kumar',
            'client_abn': '',
            'client_address': '67 Stirling Highway, Nedlands WA 6009',
            'payment_terms': 'Payment due within 14 days',
            'items': [
                {
                    'description': '1-bedroom apartment move',
                    'quantity': 1,
                    'unit_price_range': (450, 600),
                    'gst_treatment': 'TAXABLE'
                }
            ]
        },
    ]
    
    def seed(self) -> None:
        self.log_info('Seeding yearly invoices...')
        
        company = Company.objects.first()
        if not company:
            self.log_error('No company found. Run company seeder first.')
            return
        
        if Invoice.objects.exists():
            self.log_info('Deleting existing invoice records...')
            Invoice.objects.all().delete()
        
        year = 2025
        total_created = 0
        
        for month in range(1, 13):
            invoices = self._generate_invoices_for_month(year, month, company)
            total_created += len(invoices)
        
        self.log_success(f'Created {total_created} invoices across 12 months')
    
    def _generate_unit_price(self, item_config: Dict) -> Decimal:
        min_price, max_price = item_config['unit_price_range']
        price = random.randint(int(min_price * 100), int(max_price * 100)) / 100
        return Decimal(str(price))
    
    def _generate_invoices_for_month(self, year: int, month: int, company: Company) -> List[Invoice]:
        invoices = []
        month_start = date(year, month, 1)
        
        num_invoices = random.randint(8, 15)
        
        for i in range(num_invoices):
            template = random.choice(self.INVOICE_TEMPLATES)
            
            issue_day = random.randint(1, 28)
            issue_date = month_start.replace(day=issue_day)
            
            status_weights = [
                ('PAID', 0.55),
                ('SENT', 0.30),
                ('DRAFT', 0.15)
            ]
            status = random.choices(
                [s[0] for s in status_weights],
                weights=[s[1] for s in status_weights]
            )[0]
            
            payment_date = None
            if status == 'PAID':
                days_to_pay = random.randint(3, 21)
                payment_date = issue_date + timedelta(days=days_to_pay)
                if payment_date.month != month:
                    payment_date = month_start.replace(day=28)
            
            invoice = Invoice.objects.create(
                company=company,
                issue_date=issue_date,
                client_type=template['client_type'],
                client_name=template['client_name'],
                client_abn=template['client_abn'],
                client_address=template['client_address'],
                status=status,
                payment_terms=template['payment_terms'],
                payment_date=payment_date,
                notes=f'Invoice for services rendered in {month_start.strftime("%B %Y")}'
            )
            
            for item_config in template['items']:
                InvoiceItem.objects.create(
                    invoice=invoice,
                    description=item_config['description'],
                    quantity=item_config['quantity'],
                    unit_price=self._generate_unit_price(item_config),
                    gst_treatment=item_config['gst_treatment']
                )
            
            invoices.append(invoice)
        
        return invoices
