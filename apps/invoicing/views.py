from django.shortcuts import redirect, get_object_or_404, render
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.http import HttpResponse, Http404, JsonResponse
from django.db.models import Q
from django.db import transaction
from datetime import datetime, date, timedelta
from django.utils import timezone
import logging

from .models import Company, Invoice, InvoiceItem
from .forms import CompanyForm, InvoiceForm, InvoiceItemFormSet
from .utils import generate_invoice_pdf
from .services import BulkPDFService, InvoicePeriodService
from .bas_service import BASReportingService
from apps.core.services.temporal_service import get_available_years

logger = logging.getLogger(__name__)


class CompanyMixin:
    def get_company(self):
        try:
            return Company.objects.get()
        except Company.DoesNotExist:
            messages.error(
                self.request,
                'Please configure your company details before creating invoices.'
            )
            logger.warning("Attempted to access invoicing without company configuration")
            return None
        except Company.MultipleObjectsReturned:
            logger.error("Multiple companies found")
            return Company.objects.first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = self.get_company()
        return context


class CompanyFormMixin:
    def form_valid(self, form):
        response = super().form_valid(form)
        action = 'created' if not self.object.pk else 'updated'
        messages.success(self.request, f'Company configuration {action} successfully.')
        logger.info(f"Company configuration {action}: {form.instance.business_name}")
        return response


class CompanyCreateView(CompanyFormMixin, CreateView):
    model = Company
    form_class = CompanyForm
    template_name = 'invoicing/company_form.html'
    success_url = reverse_lazy('invoicing:invoice_list')
    
    def dispatch(self, request, *args, **kwargs):
        if Company.objects.exists():
            messages.info(request, 'Company already configured. Edit existing company details.')
            return redirect('invoicing:company_edit')
        return super().dispatch(request, *args, **kwargs)


class CompanyUpdateView(CompanyFormMixin, UpdateView):
    model = Company
    form_class = CompanyForm
    template_name = 'invoicing/company_form.html'
    success_url = reverse_lazy('invoicing:invoice_list')
    
    def get_object(self):
        try:
            return Company.objects.get()
        except Company.DoesNotExist:
            raise Http404("No company configuration found.")
            
    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            messages.error(request, 'No company configuration found.')
            return redirect('invoicing:company_create')
        return super().get(request, *args, **kwargs)


class InvoiceListView(ListView):
    model = Invoice
    template_name = 'invoicing/invoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 20
    ordering = ['-issue_date', '-id']

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        status = self.request.GET.get('status')
        period = self.request.GET.get('period', 'current_month')
        
        if search:
            queryset = queryset.filter(
                Q(reference__icontains=search) |
                Q(client_name__icontains=search) |
                Q(client_abn__icontains=search)
            )
        
        if status:
            queryset = queryset.filter(status=status)
            
        queryset = self._apply_period_filter(queryset, period)
        
        return queryset

    def _apply_period_filter(self, queryset, period_type):
        today = timezone.now().date()
        
        period_filters = {
            'current_month': lambda: (today.replace(day=1), today),
            'last_month': lambda: self._get_last_month_range(today),
            'current_year': lambda: (today.replace(month=1, day=1), today),
            'last_year': lambda: (date(today.year - 1, 1, 1), date(today.year - 1, 12, 31)),
            'last_3_months': lambda: (today - timedelta(days=90), today),
            'last_6_months': lambda: (today - timedelta(days=180), today),
            'last_12_months': lambda: (today - timedelta(days=365), today),
        }
        
        if period_type in period_filters:
            start, end = period_filters[period_type]()
            return queryset.filter(issue_date__range=[start, end])
        
        return queryset

    @staticmethod
    def _get_last_month_range(today):
        last_month = today.replace(day=1) - timedelta(days=1)
        return last_month.replace(day=1), last_month

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        context.update({
            'search': self.request.GET.get('search', ''),
            'status': self.request.GET.get('status', ''),
            'period': self.request.GET.get('period', 'current_month'),
            'has_company': Company.objects.exists(),
            'current_year': now.year,
            'current_month': now.month,
            'current_quarter': (now.month - 1) // 3 + 1,
            'available_years': get_available_years(),
            'available_periods': [
                ('current_month', 'Current month'),
                ('last_month', 'Last month'),
                ('current_year', 'Current year'),
                ('last_year', 'Last year'),
                ('last_3_months', 'Last 3 months'),
                ('last_6_months', 'Last 6 months'),
                ('last_12_months', 'Last 12 months'),
                ('all_time', 'All time'),
            ]
        })
        return context


class InvoiceDetailView(DetailView):
    model = Invoice
    template_name = 'invoicing/invoice_detail.html'
    context_object_name = 'invoice'


class InvoiceCreateView(CompanyMixin, CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'invoicing/invoice_form.html'

    def dispatch(self, request, *args, **kwargs):
        if not self.get_company():
            return redirect('invoicing:company_create')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = self.get_company()
        
        if self.request.POST:
            context['formset'] = InvoiceItemFormSet(
                self.request.POST,
                instance=self.object
            )
        else:
            context['formset'] = InvoiceItemFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        if not formset.is_valid():
            logger.error(f"Formset validation failed: {formset.errors}")
            return self.form_invalid(form)
        
        with transaction.atomic():
            form.instance.company = self.get_company()
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            
            logger.info(f"Invoice created: {self.object.reference or 'DRAFT'} for {self.object.client_name}")
            messages.success(
                self.request,
                f'Invoice {self.object.reference or "draft"} created successfully.'
            )
        
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('invoicing:invoice_detail', kwargs={'pk': self.object.pk})


class InvoiceUpdateView(UpdateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'invoicing/invoice_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = self.object.company
        context['is_edit'] = True
        
        if self.request.POST:
            context['formset'] = InvoiceItemFormSet(
                self.request.POST,
                instance=self.object
            )
        else:
            context['formset'] = InvoiceItemFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        with transaction.atomic():
            old_status = self.object.status if self.object else None
            self.object = form.save()
            
            if formset.is_valid():
                formset.save()
                
                if old_status == 'DRAFT' and self.object.status != 'DRAFT':
                    self.object.assign_reference_if_needed()
                    self.object.save(update_fields=['reference'])
                
                logger.info(f"Invoice updated: {self.object.reference or 'DRAFT'} for {self.object.client_name}")
                messages.success(
                    self.request,
                    f'Invoice {self.object.reference or "draft"} updated successfully.'
                )
                return redirect(self.get_success_url())
            else:
                return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('invoicing:invoice_detail', kwargs={'pk': self.object.pk})


def generate_pdf_view(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    try:
        pdf_content = generate_invoice_pdf(invoice)
        
        response = HttpResponse(pdf_content, content_type='application/pdf')
        filename = f'invoice_{invoice.reference or "draft"}.pdf'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        logger.info(f"PDF generated for invoice: {invoice.reference or 'DRAFT'}")
        return response
    except Exception as e:
        logger.error(f"Error generating PDF for invoice {invoice.reference or 'DRAFT'}: {str(e)}")
        messages.error(request, f'Error generating PDF: {str(e)}')
        return redirect('invoicing:invoice_detail', pk=pk)


def bulk_download_monthly_view(request):
    return _handle_bulk_download(
        request=request,
        period_type='monthly',
        year=int(request.GET.get('year', timezone.now().year)),
        month=int(request.GET.get('month', timezone.now().month)),
        quarter=None,
        status=request.GET.get('status', None)
    )


def bulk_download_quarterly_view(request):
    return _handle_bulk_download(
        request=request,
        period_type='quarterly',
        year=int(request.GET.get('year', timezone.now().year)),
        month=None,
        quarter=int(request.GET.get('quarter', (timezone.now().month - 1) // 3 + 1)),
        status=request.GET.get('status', None)
    )


def _handle_bulk_download(request, period_type, year, month, quarter, status):
    try:
        invoices = InvoicePeriodService.get_period_invoices(
            period_type=period_type,
            year=year,
            month=month,
            quarter=quarter,
            status=status
        )
        
        if not invoices.exists():
            period_label = _get_period_label(period_type, year, month, quarter)
            status_text = _get_status_text(status)
            messages.warning(request, f'No{status_text} invoices found for {period_label}')
            return redirect('invoicing:invoice_list')
        
        zip_prefix, filename, period_label = _get_file_info(period_type, year, month, quarter)
        
        zip_content, success_count, error_count = BulkPDFService.generate_bulk_pdfs_zip(
            invoices,
            zip_prefix
        )
        
        if not zip_content:
            messages.error(request, 'Error generating ZIP file')
            return redirect('invoicing:invoice_list')
        
        _add_download_message(request, success_count, error_count, period_label)
        logger.info(f"Bulk {period_type} download: {success_count} invoices for {period_label}")
        
        return BulkPDFService.create_zip_response(zip_content, filename)
        
    except Exception as e:
        logger.error(f"Error in bulk {period_type} download: {str(e)}")
        messages.error(request, f'Error generating bulk download: {str(e)}')
        return redirect('invoicing:invoice_list')


def _get_period_label(period_type, year, month, quarter):
    if period_type == 'monthly':
        month_names = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        return f'{month_names[month-1]} {year}'
    else:
        return f'Q{quarter} {year}'


def _get_file_info(period_type, year, month, quarter):
    if period_type == 'monthly':
        month_names_lower = [
            'january', 'february', 'march', 'april', 'may', 'june',
            'july', 'august', 'september', 'october', 'november', 'december'
        ]
        month_name = month_names_lower[month-1]
        return (
            f"invoices_{year}_{month:02d}",
            f"invoices_{month_name}_{year}.zip",
            f"{month_name} {year}"
        )
    else:
        return (
            f"invoices_{year}_Q{quarter}",
            f"invoices_Q{quarter}_{year}.zip",
            f"Q{quarter} {year}"
        )


def bulk_preview_view(request):
    period_type = request.GET.get('type')
    year = int(request.GET.get('year', timezone.now().year))
    status = request.GET.get('status', None)
    
    try:
        if period_type == 'monthly':
            month = int(request.GET.get('month', timezone.now().month))
            invoices = InvoicePeriodService.get_period_invoices('monthly', year=year, month=month, status=status)
            period_name = f"{InvoicePeriodService.MONTH_NAMES[month-1][1]} {year}"
        elif period_type == 'quarterly':
            quarter = int(request.GET.get('quarter', (timezone.now().month - 1) // 3 + 1))
            invoices = InvoicePeriodService.get_period_invoices('quarterly', year=year, quarter=quarter, status=status)
            period_name = f"Q{quarter} {year}"
        else:
            return JsonResponse({'error': 'Invalid period type'}, status=400)
        
        summary = InvoicePeriodService.get_period_summary(invoices)
        
        return JsonResponse({
            'count': summary['count'],
            'total_amount': summary['total_amount'],
            'date_range': summary['date_range'],
            'period_name': period_name,
            'success': True
        })
        
    except Exception as e:
        logger.error(f"Error in bulk preview: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


def _get_status_text(status):
    status_texts = {
        'SENT': ' sent',
        'PAID': ' paid',
    }
    return status_texts.get(status, ' sent or paid')


def _add_download_message(request, success_count, error_count, period):
    if error_count > 0:
        messages.warning(
            request,
            f'Download complete: {success_count} invoices generated, {error_count} errors'
        )
    else:
        messages.success(
            request,
            f'Download complete: {success_count} invoices for {period}'
        )


@login_required
def bas_report_view(request):
    period_type = request.GET.get('type', 'quarterly')
    year = int(request.GET.get('year', timezone.now().year))
    month = None
    quarter = None
    
    try:
        if period_type == 'monthly':
            month = int(request.GET.get('month', timezone.now().month))
            report_data = BASReportingService.get_monthly_gst_report(year, month)
        elif period_type == 'quarterly':
            quarter = int(request.GET.get('quarter', (timezone.now().month - 1) // 3 + 1))
            report_data = BASReportingService.get_quarterly_gst_report(year, quarter)
        elif period_type == 'annual':
            report_data = BASReportingService.get_annual_gst_summary(year)
        else:
            messages.error(request, 'Invalid period type')
            return redirect('invoicing:invoice_list')
        
        context = {
            'report_data': report_data,
            'period_type': period_type,
            'year': year,
            'available_years': get_available_years(),
            'current_year': timezone.now().year,
            'current_quarter': (timezone.now().month - 1) // 3 + 1,
            'current_month': timezone.now().month,
        }
        
        if month is not None:
            context['month'] = month
        if quarter is not None:
            context['quarter'] = quarter
        
        logger.info(f"BAS report generated: {period_type} for {year}")
        return render(request, 'invoicing/bas_report.html', context)
        
    except Exception as e:
        logger.error(f"Error generating BAS report: {str(e)}")
        messages.error(request, f'Error generating BAS report: {str(e)}')
        return redirect('invoicing:invoice_list')


@login_required
def bas_pdf_view(request):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    from io import BytesIO
    
    period_type = request.GET.get('type', 'quarterly')
    year = int(request.GET.get('year', timezone.now().year))
    
    try:
        if period_type == 'monthly':
            month = int(request.GET.get('month', timezone.now().month))
            report_data = BASReportingService.get_monthly_gst_report(year, month)
        elif period_type == 'quarterly':
            quarter = int(request.GET.get('quarter', (timezone.now().month - 1) // 3 + 1))
            report_data = BASReportingService.get_quarterly_gst_report(year, quarter)
        elif period_type == 'annual':
            report_data = BASReportingService.get_annual_gst_summary(year)
        else:
            messages.error(request, 'Invalid period type')
            return redirect('invoicing:bas_report')
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
        
        elements = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1e3a8a'),
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        elements.append(Paragraph('Business Activity Statement (BAS)', title_style))
        elements.append(Paragraph(f'Period: {report_data["period"]}', styles['Normal']))
        elements.append(Spacer(1, 0.5*cm))
        
        company = Company.objects.first()
        if company:
            elements.append(Paragraph(f'<b>{company.business_name}</b>', styles['Normal']))
            elements.append(Paragraph(f'ABN: {company.abn}', styles['Normal']))
            elements.append(Spacer(1, 0.5*cm))
        
        bas_data = [
            ['Field', 'Description', 'Amount (AUD)'],
            ['G1', 'Total Sales (inc GST)', f"${report_data['G1_total_sales_inc_gst']:,.2f}"],
            ['G2', 'Export Sales', f"${report_data['G2_export_sales']:,.2f}"],
            ['G3', 'GST-Free Sales', f"${report_data['G3_gst_free_sales']:,.2f}"],
            ['G4', 'Input Taxed Sales', f"${report_data.get('G4_input_taxed_sales', 0):,.2f}"],
            ['1A', 'GST on Sales', f"${report_data['1A_gst_on_sales']:,.2f}"],
        ]
        
        table = Table(bas_data, colWidths=[2*cm, 10*cm, 4*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.5*cm))
        
        summary_data = [
            ['Total Sales (ex GST)', f"${report_data.get('total_sales_ex_gst', 0):,.2f}"],
            ['GST Collected', f"${report_data['1A_gst_on_sales']:,.2f}"],
            ['Invoice Count', str(report_data['invoice_count'])],
        ]
        
        summary_table = Table(summary_data, colWidths=[10*cm, 4*cm])
        summary_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 1*cm))
        
        footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey)
        elements.append(Paragraph(f'Generated: {timezone.now().strftime("%d/%m/%Y %H:%M")}', footer_style))
        
        doc.build(elements)
        pdf_content = buffer.getvalue()
        buffer.close()
        
        response = HttpResponse(pdf_content, content_type='application/pdf')
        filename = f'BAS_{period_type}_{year}.pdf'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        logger.info(f"BAS PDF generated: {period_type} for {year}")
        return response
        
    except Exception as e:
        logger.error(f"Error generating BAS PDF: {str(e)}")
        messages.error(request, f'Error generating BAS PDF: {str(e)}')
        return redirect('invoicing:bas_report')
