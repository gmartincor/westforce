from django.shortcuts import redirect, get_object_or_404
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.contrib import messages
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
        context.update({
            'search': self.request.GET.get('search', ''),
            'status': self.request.GET.get('status', ''),
            'period': self.request.GET.get('period', 'current_month'),
            'has_company': Company.objects.exists(),
            'current_year': timezone.now().year,
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
        
        if formset.is_valid():
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
        
        return self.form_invalid(form)

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
    year = int(request.GET.get('year', timezone.now().year))
    month = int(request.GET.get('month', timezone.now().month))
    status = request.GET.get('status', None)
    
    try:
        invoices = InvoicePeriodService.get_period_invoices('monthly', year=year, month=month, status=status)
        
        if not invoices.exists():
            status_text = _get_status_text(status)
            messages.warning(request, f'No{status_text} invoices found for {month:02d}/{year}')
            return redirect('invoicing:invoice_list')
        
        zip_content, success_count, error_count = BulkPDFService.generate_bulk_pdfs_zip(
            invoices,
            f"invoices_{year}_{month:02d}"
        )
        
        if not zip_content:
            messages.error(request, 'Error generating ZIP file')
            return redirect('invoicing:invoice_list')
        
        month_names = [
            'january', 'february', 'march', 'april', 'may', 'june',
            'july', 'august', 'september', 'october', 'november', 'december'
        ]
        
        filename = f"invoices_{month_names[month-1]}_{year}.zip"
        
        _add_download_message(request, success_count, error_count, f'{month_names[month-1]} {year}')
        logger.info(f"Bulk monthly download: {success_count} invoices for {month:02d}/{year}")
        
        return BulkPDFService.create_zip_response(zip_content, filename)
        
    except Exception as e:
        logger.error(f"Error in bulk monthly download: {str(e)}")
        messages.error(request, f'Error generating bulk download: {str(e)}')
        return redirect('invoicing:invoice_list')


def bulk_download_quarterly_view(request):
    year = int(request.GET.get('year', timezone.now().year))
    quarter = int(request.GET.get('quarter', (timezone.now().month - 1) // 3 + 1))
    status = request.GET.get('status', None)
    
    try:
        invoices = InvoicePeriodService.get_period_invoices('quarterly', year=year, quarter=quarter, status=status)
        
        if not invoices.exists():
            status_text = _get_status_text(status)
            messages.warning(request, f'No{status_text} invoices found for Q{quarter}/{year}')
            return redirect('invoicing:invoice_list')
        
        zip_content, success_count, error_count = BulkPDFService.generate_bulk_pdfs_zip(
            invoices,
            f"invoices_{year}_Q{quarter}"
        )
        
        if not zip_content:
            messages.error(request, 'Error generating ZIP file')
            return redirect('invoicing:invoice_list')
        
        filename = f"invoices_Q{quarter}_{year}.zip"
        
        _add_download_message(request, success_count, error_count, f'Q{quarter} {year}')
        logger.info(f"Bulk quarterly download: {success_count} invoices for Q{quarter}/{year}")
        
        return BulkPDFService.create_zip_response(zip_content, filename)
        
    except Exception as e:
        logger.error(f"Error in bulk quarterly download: {str(e)}")
        messages.error(request, f'Error generating bulk download: {str(e)}')
        return redirect('invoicing:invoice_list')


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
