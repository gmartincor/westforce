from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Sum, Count

from .models import Income
from .services import IncomeService
from .forms import IncomeFilterForm


INCOME_FIELDS = [
    'service_type', 'amount', 'date', 'payment_method',
    'client_name', 'pickup_address', 'delivery_address',
    'description', 'reference_number'
]


class IncomeListView(LoginRequiredMixin, ListView):
    model = Income
    template_name = 'accounting/income_list.html'
    context_object_name = 'incomes'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = Income.objects.order_by('-date')
        form = IncomeFilterForm(self.request.GET)
        
        if form.is_valid():
            if date_from := form.cleaned_data.get('date_from'):
                queryset = queryset.filter(date__gte=date_from)
            
            if date_to := form.cleaned_data.get('date_to'):
                queryset = queryset.filter(date__lte=date_to)
            
            if client_name := form.cleaned_data.get('client_name'):
                queryset = queryset.filter(client_name__icontains=client_name)
            
            if amount_min := form.cleaned_data.get('amount_min'):
                queryset = queryset.filter(amount__gte=amount_min)
            
            if amount_max := form.cleaned_data.get('amount_max'):
                queryset = queryset.filter(amount__lte=amount_max)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = IncomeFilterForm(self.request.GET)
        
        page_incomes = context.get('incomes', [])
        if page_incomes:
            total = sum(income.amount for income in page_incomes)
            count = len(page_incomes)
            context.update({
                'total_amount': total,
                'income_count': count,
                'average_amount': total / count
            })
        else:
            context.update({
                'total_amount': 0,
                'income_count': 0,
                'average_amount': 0
            })
        
        return context


class IncomeCreateView(LoginRequiredMixin, CreateView):
    model = Income
    template_name = 'accounting/income_form.html'
    fields = INCOME_FIELDS
    success_url = reverse_lazy('accounting:income_list')


class IncomeUpdateView(LoginRequiredMixin, UpdateView):
    model = Income
    template_name = 'accounting/income_form.html'
    fields = INCOME_FIELDS
    success_url = reverse_lazy('accounting:income_list')


class IncomeDeleteView(LoginRequiredMixin, DeleteView):
    model = Income
    template_name = 'accounting/income_confirm_delete.html'
    success_url = reverse_lazy('accounting:income_list')


@login_required
def revenue_summary_view(request):
    year = int(request.GET.get('year', timezone.now().year))
    service = IncomeService()
    
    summary = service.get_revenue_summary(year)
    
    monthly_trends = Income.objects.filter(
        accounting_year=year
    ).values('accounting_month').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('accounting_month')
    
    service_breakdown = Income.objects.filter(
        accounting_year=year
    ).values('service_type').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    context = {
        'page_title': 'Revenue Summary',
        'page_subtitle': f'Revenue analysis for {year}',
        'summary': summary,
        'monthly_trends': monthly_trends,
        'service_breakdown': service_breakdown,
        'selected_year': year,
    }
    
    return render(request, 'accounting/revenue_summary.html', context)


@login_required
def profit_summary_view(request):
    year = int(request.GET.get('year', timezone.now().year))
    service = IncomeService()
    
    summary = service.get_profit_summary(year)
    
    context = {
        'page_title': 'Profit Analysis',
        'page_subtitle': f'Profit analysis for {year}',
        'summary': summary,
        'selected_year': year,
    }
    
    return render(request, 'accounting/profit_summary.html', context)
