from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Sum, Count

from .models import Income
from .services import IncomeService
from .forms import IncomeFilterForm, ProfitFilterForm


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
def profit_summary_view(request):
    form = ProfitFilterForm(request.GET)
    service = IncomeService()
    
    filter_params = {}
    
    if form.is_valid():
        if date_from := form.cleaned_data.get('date_from'):
            filter_params['date_from'] = date_from
        
        if date_to := form.cleaned_data.get('date_to'):
            filter_params['date_to'] = date_to
        
        if service_types := form.cleaned_data.get('service_types'):
            filter_params['service_types'] = service_types
        
        if expense_categories := form.cleaned_data.get('expense_categories'):
            filter_params['expense_categories'] = expense_categories
    
    summary = service.get_profit_summary(**filter_params)
    
    context = {
        'page_title': 'Profit Analysis',
        'page_subtitle': 'Comprehensive profit analysis with filters',
        'summary': summary,
        'filter_form': form,
    }
    
    return render(request, 'accounting/profit_summary.html', context)
