from decimal import Decimal
from datetime import date, timedelta
from django.db.models import Sum, Q, Case, When, DecimalField
from django.utils import timezone

from .models import Invoice, InvoiceItem


class BASReportingService:
    
    @classmethod
    def get_quarterly_gst_report(cls, year, quarter):
        start_date, end_date = cls._get_quarter_dates(year, quarter)
        
        invoices = Invoice.objects.filter(
            issue_date__range=[start_date, end_date],
            status__in=['SENT', 'PAID', 'OVERDUE']
        ).prefetch_related('items')
        
        bas_data = cls._calculate_bas_fields(invoices)
        
        return {
            'period': f'Q{quarter} {year}',
            'start_date': start_date,
            'end_date': end_date,
            'invoice_count': invoices.count(),
            **bas_data
        }
    
    @classmethod
    def get_monthly_gst_report(cls, year, month):
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        invoices = Invoice.objects.filter(
            issue_date__range=[start_date, end_date],
            status__in=['SENT', 'PAID', 'OVERDUE']
        ).prefetch_related('items')
        
        bas_data = cls._calculate_bas_fields(invoices)
        
        return {
            'period': f'{month:02d}/{year}',
            'start_date': start_date,
            'end_date': end_date,
            'invoice_count': invoices.count(),
            **bas_data
        }
    
    @classmethod
    def get_annual_gst_summary(cls, year):
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        
        invoices = Invoice.objects.filter(
            issue_date__range=[start_date, end_date],
            status__in=['SENT', 'PAID', 'OVERDUE']
        ).prefetch_related('items')
        
        quarterly_data = []
        for quarter in range(1, 5):
            q_data = cls.get_quarterly_gst_report(year, quarter)
            quarterly_data.append(q_data)
        
        total_g1 = sum(q['G1_total_sales_inc_gst'] for q in quarterly_data)
        total_g2 = sum(q['G2_export_sales'] for q in quarterly_data)
        total_g3 = sum(q['G3_gst_free_sales'] for q in quarterly_data)
        total_1a = sum(q['1A_gst_on_sales'] for q in quarterly_data)
        
        return {
            'year': year,
            'quarterly_breakdown': quarterly_data,
            'annual_G1_total_sales_inc_gst': total_g1,
            'annual_G2_export_sales': total_g2,
            'annual_G3_gst_free_sales': total_g3,
            'annual_1A_gst_on_sales': total_1a,
            'total_invoice_count': invoices.count(),
        }
    
    @classmethod
    def _calculate_bas_fields(cls, invoices):
        g1_total = Decimal('0.00')
        g2_export = Decimal('0.00')
        g3_gst_free = Decimal('0.00')
        g4_input_taxed = Decimal('0.00')
        gst_on_sales = Decimal('0.00')
        taxable_sales = Decimal('0.00')
        
        for invoice in invoices:
            invoice_total = invoice.total_amount
            invoice_gst = invoice.gst_amount
            invoice_subtotal = invoice.subtotal
            
            has_gst_free = False
            has_input_taxed = False
            
            for item in invoice.items.all():
                if item.gst_treatment == 'GST_FREE':
                    has_gst_free = True
                    g3_gst_free += item.subtotal
                elif item.gst_treatment == 'INPUT_TAXED':
                    has_input_taxed = True
                    g4_input_taxed += item.subtotal
            
            g1_total += invoice_total
            gst_on_sales += invoice_gst
            
            if not has_gst_free and not has_input_taxed:
                taxable_sales += invoice_subtotal
        
        return {
            'G1_total_sales_inc_gst': g1_total,
            'G2_export_sales': g2_export,
            'G3_gst_free_sales': g3_gst_free,
            'G4_input_taxed_sales': g4_input_taxed,
            '1A_gst_on_sales': gst_on_sales,
            'taxable_sales_ex_gst': taxable_sales,
            'total_sales_ex_gst': taxable_sales + g3_gst_free + g4_input_taxed,
        }
    
    @staticmethod
    def _get_quarter_dates(year, quarter):
        start_month = (quarter - 1) * 3 + 1
        start_date = date(year, start_month, 1)
        
        if quarter == 4:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_month = start_month + 2
            next_month = end_month + 1
            if next_month > 12:
                end_date = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(year, next_month, 1) - timedelta(days=1)
        
        return start_date, end_date
