from decimal import Decimal
from datetime import date, timedelta
from django.db.models import Sum, Q
from django.utils import timezone

from .models import Invoice


class BASReportingService:
    
    @classmethod
    def get_quarterly_gst_report(cls, year, quarter):
        start_date, end_date = cls._get_quarter_dates(year, quarter)
        
        invoices = Invoice.objects.filter(
            issue_date__range=[start_date, end_date],
            status__in=['SENT', 'PAID']
        ).prefetch_related('items')
        
        total_sales = Decimal('0.00')
        gst_on_sales = Decimal('0.00')
        
        for invoice in invoices:
            total_sales += invoice.subtotal
            gst_on_sales += invoice.gst_amount
        
        return {
            'period': f'Q{quarter} {year}',
            'start_date': start_date,
            'end_date': end_date,
            'total_sales_excluding_gst': total_sales,
            'gst_on_sales': gst_on_sales,
            'total_sales_including_gst': total_sales + gst_on_sales,
            'invoice_count': invoices.count(),
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
            status__in=['SENT', 'PAID']
        ).prefetch_related('items')
        
        total_sales = Decimal('0.00')
        gst_on_sales = Decimal('0.00')
        
        for invoice in invoices:
            total_sales += invoice.subtotal
            gst_on_sales += invoice.gst_amount
        
        return {
            'period': f'{month:02d}/{year}',
            'start_date': start_date,
            'end_date': end_date,
            'total_sales_excluding_gst': total_sales,
            'gst_on_sales': gst_on_sales,
            'total_sales_including_gst': total_sales + gst_on_sales,
            'invoice_count': invoices.count(),
        }
    
    @classmethod
    def get_annual_gst_summary(cls, year):
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        
        invoices = Invoice.objects.filter(
            issue_date__range=[start_date, end_date],
            status__in=['SENT', 'PAID']
        ).prefetch_related('items')
        
        quarterly_data = []
        for quarter in range(1, 5):
            q_data = cls.get_quarterly_gst_report(year, quarter)
            quarterly_data.append(q_data)
        
        total_sales = sum(q['total_sales_excluding_gst'] for q in quarterly_data)
        total_gst = sum(q['gst_on_sales'] for q in quarterly_data)
        
        return {
            'year': year,
            'quarterly_breakdown': quarterly_data,
            'annual_total_sales_excluding_gst': total_sales,
            'annual_gst_on_sales': total_gst,
            'annual_total_sales_including_gst': total_sales + total_gst,
            'total_invoice_count': invoices.count(),
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
