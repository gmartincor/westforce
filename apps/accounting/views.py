from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Sum, Count
from django.utils import timezone

from .models import Income
from .services import AccountingService


class IncomeListView(LoginRequiredMixin, ListView):
    model = Income
    template_name = 'accounting/income_list.html'
    context_object_name = 'incomes'
    paginate_by = 25
    
    def get_queryset(self):
        return Income.objects.order_by('-date')


class IncomeCreateView(LoginRequiredMixin, CreateView):
    model = Income
    template_name = 'accounting/income_form.html'
    fields = ['service_type', 'amount', 'date', 'payment_method', 
              'client_name', 'pickup_address', 'delivery_address', 'description', 'reference_number']
    success_url = reverse_lazy('accounting:income_list')


class IncomeUpdateView(LoginRequiredMixin, UpdateView):
    model = Income
    template_name = 'accounting/income_form.html'
    fields = ['service_type', 'amount', 'date', 'payment_method', 
              'client_name', 'pickup_address', 'delivery_address', 'description', 'reference_number']
    success_url = reverse_lazy('accounting:income_list')


class IncomeDeleteView(LoginRequiredMixin, DeleteView):
    model = Income
    template_name = 'accounting/income_confirm_delete.html'
    success_url = reverse_lazy('accounting:income_list')


@login_required
def revenue_summary_view(request):
    current_year = timezone.now().year
    year = int(request.GET.get('year', current_year))
    
    accounting_service = AccountingService()
    summary = accounting_service.get_revenue_summary(year)
    
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
    current_year = timezone.now().year
    year = int(request.GET.get('year', current_year))
    
    accounting_service = AccountingService()
    summary = accounting_service.get_profit_summary(year)
    
    context = {
        'page_title': 'Profit Analysis',
        'page_subtitle': f'Profit analysis for {year}',
        'summary': summary,
        'selected_year': year,
    }
    
    return render(request, 'accounting/profit_summary.html', context)
