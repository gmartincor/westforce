from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Sum, Count
from django.utils import timezone

from .models import Income
from .services import AccountingService
from apps.business_lines.models import BusinessLine
from apps.business_lines.services import BusinessLineService


class IncomeListView(LoginRequiredMixin, ListView):
    model = Income
    template_name = 'accounting/income_list.html'
    context_object_name = 'incomes'
    paginate_by = 25
    
    def get_queryset(self):
        return Income.objects.select_related('business_line').order_by('-date')


class IncomeCreateView(LoginRequiredMixin, CreateView):
    model = Income
    template_name = 'accounting/income_form.html'
    fields = ['business_line', 'service_type', 'amount', 'date', 'payment_method', 
              'client_name', 'pickup_address', 'delivery_address', 'description', 'reference_number']
    success_url = reverse_lazy('accounting:income_list')


class IncomeUpdateView(LoginRequiredMixin, UpdateView):
    model = Income
    template_name = 'accounting/income_form.html'
    fields = ['business_line', 'service_type', 'amount', 'date', 'payment_method', 
              'client_name', 'pickup_address', 'delivery_address', 'description', 'reference_number']
    success_url = reverse_lazy('accounting:income_list')


class IncomeDeleteView(LoginRequiredMixin, DeleteView):
    model = Income
    template_name = 'accounting/income_confirm_delete.html'
    success_url = reverse_lazy('accounting:income_list')


@login_required
def business_lines_view(request):
    business_line_service = BusinessLineService()
    accounting_service = AccountingService()
    
    context = {
        'business_lines': business_line_service.get_business_lines_tree(),
        'income_stats': accounting_service.get_business_line_income_stats(),
    }
    
    return render(request, 'accounting/business_lines.html', context)


@login_required
def revenue_summary_view(request, category):
    current_year = timezone.now().year
    
    total_summary = Income.objects.filter(
        accounting_year=current_year
    ).aggregate(
        total_amount=Sum('amount'),
        total_payments=Count('id')
    )
    
    if total_summary['total_payments'] and total_summary['total_payments'] > 0:
        total_summary['average_amount'] = total_summary['total_amount'] / total_summary['total_payments']
    else:
        total_summary['average_amount'] = 0
    
    business_lines = BusinessLine.objects.filter(is_active=True)
    revenue_data = []
    
    for bl in business_lines:
        income_data = Income.objects.filter(
            business_line=bl,
            accounting_year=current_year
        ).aggregate(
            total=Sum('amount'),
            count=Count('id')
        )
        
        if income_data['count'] and income_data['count'] > 0:
            revenue_data.append({
                'business_line': bl,
                'total_amount': income_data['total'] or 0,
                'total_payments': income_data['count'],
                'average_amount': (income_data['total'] or 0) / income_data['count'],
                'level': bl.level,
            })
    
    monthly_trends = Income.objects.filter(
        accounting_year=current_year
    ).extra(
        select={'month': "DATE_TRUNC('month', date)"}
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')
    
    context = {
        'category': category,
        'category_display': category.title(),
        'page_title': f'Revenue Summary - {category.title()}',
        'page_subtitle': f'Revenue analysis for {current_year}',
        'revenue_data': revenue_data,
        'total_summary': total_summary,
        'monthly_trends': monthly_trends,
        'selected_year': current_year,
    }
    
    return render(request, 'accounting/revenue_summary.html', context)


@login_required
def profit_summary_view(request, category):
    current_year = timezone.now().year
    
    total_revenue = Income.objects.filter(
        accounting_year=current_year
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    try:
        from apps.expenses.models import Expense
        total_expenses = Expense.objects.filter(
            date__year=current_year,
            service_category=category
        ).aggregate(total=Sum('amount'))['total'] or 0
    except ImportError:
        total_expenses = 0
    
    revenue_stats = Income.objects.filter(
        accounting_year=current_year
    ).aggregate(
        total_payments=Count('id')
    )
    
    profit = total_revenue - total_expenses
    
    context = {
        'category': category,
        'category_display': category.title(),
        'page_title': f'Profit Analysis - {category.title()}',
        'page_subtitle': f'Profit analysis for {current_year}',
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'profit': profit,
        'revenue_stats': revenue_stats,
        'selected_year': current_year,
    }
    
    return render(request, 'accounting/profit_summary.html', context)
