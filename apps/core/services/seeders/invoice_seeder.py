from datetime import date, timedelta
from decimal import Decimal
from typing import List, Dict, Any
from apps.invoicing.models import Company, Invoice, InvoiceItem
from .base_seeder import BaseSeeder


class InvoiceSeeder(BaseSeeder):
    
    def _get_invoice_items_data(self) -> Dict[str, List[Dict[str, Any]]]:
        return {
            'invoice_1': [
                {
                    'description': '2-bedroom apartment move - labour and truck hire',
                    'quantity': 1,
                    'unit_price': Decimal('590.91'),
                    'gst_treatment': 'TAXABLE'
                }
            ],
            'invoice_2': [
                {
                    'description': 'Office relocation - 50 desks',
                    'quantity': 50,
                    'unit_price': Decimal('15.00'),
                    'gst_treatment': 'TAXABLE'
                },
                {
                    'description': 'IT equipment transport and setup',
                    'quantity': 1,
                    'unit_price': Decimal('681.82'),
                    'gst_treatment': 'TAXABLE'
                }
            ],
            'invoice_3': [
                {
                    'description': 'Storage rental - 2 months',
                    'quantity': 2,
                    'unit_price': Decimal('100.00'),
                    'gst_treatment': 'TAXABLE'
                }
            ],
            'invoice_4': [
                {
                    'description': 'Interstate move Perth to Melbourne - 3-bedroom house',
                    'quantity': 1,
                    'unit_price': Decimal('2545.45'),
                    'gst_treatment': 'TAXABLE'
                }
            ],
            'invoice_5': [
                {
                    'description': 'Professional packing service - fragile items',
                    'quantity': 1,
                    'unit_price': Decimal('345.45'),
                    'gst_treatment': 'TAXABLE'
                }
            ],
        }
    
    def _get_invoices_data(self, company: Company) -> List[Dict[str, Any]]:
        today = date.today()
        return [
            {
                'key': 'invoice_1',
                'company': company,
                'issue_date': today - timedelta(days=35),
                'client_type': 'INDIVIDUAL',
                'client_name': 'Sarah Johnson',
                'client_abn': '',
                'client_address': '25 Murray Street, Perth WA 6000',
                'status': 'PAID',
                'payment_terms': 'Payment due within 14 days',
                'payment_date': today - timedelta(days=25),
                'notes': 'Repeat customer - excellent feedback'
            },
            {
                'key': 'invoice_2',
                'company': company,
                'issue_date': today - timedelta(days=30),
                'client_type': 'BUSINESS',
                'client_name': 'Perth Legal Associates Pty Ltd',
                'client_abn': '51987654321',
                'client_address': 'Level 3, 89 St Georges Terrace, Perth WA 6000',
                'status': 'PAID',
                'payment_terms': 'Payment due within 30 days',
                'payment_date': today - timedelta(days=15),
                'notes': 'Corporate client - monthly retainer'
            },
            {
                'key': 'invoice_3',
                'company': company,
                'issue_date': today - timedelta(days=20),
                'client_type': 'INDIVIDUAL',
                'client_name': 'Michael Chen',
                'client_abn': '',
                'client_address': '12 Kings Park Road, West Perth WA 6005',
                'status': 'SENT',
                'payment_terms': 'Payment due within 14 days',
                'notes': 'Storage arrangement - auto-renew'
            },
            {
                'key': 'invoice_4',
                'company': company,
                'issue_date': today - timedelta(days=15),
                'client_type': 'INDIVIDUAL',
                'client_name': 'Emma Thompson',
                'client_abn': '',
                'client_address': '15 South Terrace, Fremantle WA 6160',
                'status': 'SENT',
                'payment_terms': 'Payment due within 7 days',
                'notes': 'Interstate move - insurance included'
            },
            {
                'key': 'invoice_5',
                'company': company,
                'issue_date': today - timedelta(days=10),
                'client_type': 'INDIVIDUAL',
                'client_name': 'Robert Wilson',
                'client_abn': '',
                'client_address': '78 Rokeby Road, Subiaco WA 6008',
                'status': 'DRAFT',
                'payment_terms': 'Payment due within 14 days',
                'notes': 'Artwork packing - handle with care'
            },
        ]
    
    def seed(self) -> None:
        self.log_info('Seeding invoices...')
        
        if Invoice.objects.exists():
            self.log_info('Invoice records already exist. Skipping.')
            return
        
        company = Company.objects.first()
        if not company:
            self.log_error('No company found. Run company seeder first.')
            return
        
        invoices_data = self._get_invoices_data(company)
        items_data = self._get_invoice_items_data()
        
        created_count = 0
        for invoice_data in invoices_data:
            key = invoice_data.pop('key')
            invoice = Invoice.objects.create(**invoice_data)
            
            if key in items_data:
                for item_data in items_data[key]:
                    InvoiceItem.objects.create(invoice=invoice, **item_data)
            
            created_count += 1
        
        self.log_success(f'Created {created_count} invoices with items')
