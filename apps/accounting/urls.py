from django.urls import path
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Income

app_name = 'accounting'

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

urlpatterns = [
    path('', IncomeListView.as_view(), name='income_list'),
    path('income/add/', IncomeCreateView.as_view(), name='income_add'),
    path('income/<int:pk>/edit/', IncomeUpdateView.as_view(), name='income_edit'),
    path('income/<int:pk>/delete/', IncomeDeleteView.as_view(), name='income_delete'),
]
