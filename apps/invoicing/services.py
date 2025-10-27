from django.http import HttpResponse
from django.utils import timezone
from datetime import date, datetime, timedelta
from decimal import Decimal
import zipfile
import io
import logging

from .models import Invoice
from .utils import generate_invoice_pdf

logger = logging.getLogger(__name__)


class InvoicePeriodService:
    MONTH_NAMES = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ]
    
    QUARTER_NAMES = [
        (1, 'Q1 (January - March)'), (2, 'Q2 (April - June)'),
        (3, 'Q3 (July - September)'), (4, 'Q4 (October - December)')
    ]
    
    @classmethod
    def get_period_invoices(cls, period_type, year=None, month=None, quarter=None, status=None):
        today = timezone.now().date()
        
        if period_type == 'monthly':
            start, end = cls._get_monthly_range(year, month, today)
        elif period_type == 'quarterly':
            start, end = cls._get_quarterly_range(year, quarter, today)
        else:
            raise ValueError(f"Invalid period type: {period_type}")
        
        queryset = Invoice.objects.filter(issue_date__range=[start, end])
        
        if status:
            queryset = queryset.filter(status=status)
        else:
            queryset = queryset.filter(status__in=['SENT', 'PAID', 'OVERDUE'])
        
        return queryset.order_by('issue_date', 'reference')
    
    @staticmethod
    def _get_monthly_range(year, month, today):
        if year and month:
            start = date(year, month, 1)
            if month == 12:
                end = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                end = date(year, month + 1, 1) - timedelta(days=1)
        else:
            start = today.replace(day=1)
            end = today
        return start, end
    
    @staticmethod
    def _get_quarterly_range(year, quarter, today):
        if year and quarter:
            start_month = (quarter - 1) * 3 + 1
            start = date(year, start_month, 1)
            if quarter == 4:
                end = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_month = start_month + 2
                next_month = end_month + 1
                if next_month > 12:
                    end = date(year + 1, 1, 1) - timedelta(days=1)
                else:
                    end = date(year, next_month, 1) - timedelta(days=1)
        else:
            current_quarter = (today.month - 1) // 3 + 1
            start_month = (current_quarter - 1) * 3 + 1
            start = date(today.year, start_month, 1)
            end = today
        return start, end
    
    @staticmethod
    def get_period_summary(invoices):
        if not invoices:
            return {
                'count': 0,
                'total_amount': '0.00',
                'date_range': 'No invoices'
            }
        
        total_amount = sum(invoice.total_amount for invoice in invoices)
        start_date = invoices.first().issue_date
        end_date = invoices.last().issue_date
        
        return {
            'count': invoices.count(),
            'total_amount': f"{total_amount:.2f}",
            'date_range': f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}"
        }


class BulkPDFService:
    @staticmethod
    def generate_bulk_pdfs_zip(invoices, filename_prefix):
        buffer = io.BytesIO()
        success_count = 0
        error_count = 0
        
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for invoice in invoices:
                try:
                    pdf_content = generate_invoice_pdf(invoice)
                    pdf_filename = f"{invoice.reference or f'draft_{invoice.id}'}.pdf"
                    zip_file.writestr(pdf_filename, pdf_content)
                    success_count += 1
                    logger.info(f"PDF added to ZIP: {pdf_filename}")
                except Exception as e:
                    error_count += 1
                    logger.error(f"Error generating PDF for invoice {invoice.id}: {str(e)}")
                    continue
        
        zip_content = buffer.getvalue()
        buffer.close()
        
        if success_count == 0:
            logger.warning("No PDFs generated for ZIP file")
            return None, 0, error_count
        
        return zip_content, success_count, error_count
    
    @staticmethod
    def create_zip_response(zip_content, filename):
        response = HttpResponse(zip_content, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
