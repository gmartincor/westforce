from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Sum, Count, Q
from django.contrib import messages
from django.shortcuts import get_object_or_404

from apps.expenses.models import Expense, ExpenseCategory
from apps.expenses.forms import ExpenseForm, ExpenseCategoryForm
from apps.core.mixins import TemporalFilterMixin
from apps.core.constants import SUCCESS_MESSAGES
from apps.core.services.temporal_service import parse_temporal_filters, get_temporal_context


class ExpenseCategoryView(LoginRequiredMixin, TemplateView):
    template_name = 'expenses/categories.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        filters = parse_temporal_filters(self.request)
        year = filters.get('year')
        month = filters.get('month')
        
        expense_filter = {}
        if year:
            expense_filter['accounting_year'] = year
        if month:
            expense_filter['accounting_month'] = month
        
        category_totals = {}
        for category_type, display_name in ExpenseCategory.CategoryTypeChoices.choices:
            total = Expense.objects.filter(
                category__category_type=category_type,
                **expense_filter
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            category_totals[category_type] = {
                'name': display_name,
                'total': total,
            }
        
        total_general = sum(total['total'] for total in category_totals.values())
        
        base_filter = Q()
        if year:
            base_filter &= Q(expenses__accounting_year=year)
        if month:
            base_filter &= Q(expenses__accounting_month=month)
        
        categories = ExpenseCategory.objects.filter(
            is_active=True
        ).annotate(
            total_amount=Sum('expenses__amount', filter=base_filter),
            expense_count=Count('expenses', filter=base_filter)
        ).order_by('category_type', 'name')
        
        context.update({
            'category_totals': category_totals,
            'total_general': total_general,
            'categories': categories,
            **get_temporal_context(year, month)
        })
        
        return context


class ExpenseListView(LoginRequiredMixin, TemporalFilterMixin, ListView):
    model = Expense
    template_name = 'expenses/expense_list.html'
    context_object_name = 'expenses'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        category_type = self.kwargs.get('category_type')
        category_slug = self.kwargs.get('category_slug')
        
        if category_slug:
            category = get_object_or_404(ExpenseCategory, slug=category_slug)
            queryset = queryset.filter(category=category)
            self.category = category
        elif category_type:
            queryset = queryset.filter(category__category_type=category_type)
        
        filters = parse_temporal_filters(self.request)
        year = filters.get('year')
        month = filters.get('month')
        
        if year:
            queryset = queryset.filter(accounting_year=year)
        if month:
            queryset = queryset.filter(accounting_month=month)
        
        return queryset.select_related('category').order_by('-date', '-created')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        category_type = self.kwargs.get('category_type')
        category_slug = self.kwargs.get('category_slug')
        
        filters = parse_temporal_filters(self.request)
        year = filters.get('year')
        month = filters.get('month')
        
        context.update({
            'category_type': category_type,
            'category_slug': category_slug,
            **get_temporal_context(year, month)
        })
        
        if hasattr(self, 'category'):
            context['category'] = self.category
        elif category_type:
            category_type_display = dict(ExpenseCategory.CategoryTypeChoices.choices).get(category_type, category_type)
            context['category_type_display'] = category_type_display
        
        expenses = context['expenses']
        if expenses:
            context['total_amount'] = sum(expense.amount for expense in expenses)
            context['expense_count'] = len(expenses)
            context['average_amount'] = context['total_amount'] / len(expenses) if len(expenses) > 0 else 0
        else:
            context['total_amount'] = 0
            context['expense_count'] = 0
            context['average_amount'] = 0
        
        return context


class ExpenseCreateView(LoginRequiredMixin, CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expenses/expense_form.html'
    success_url = reverse_lazy('expenses:categories')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        category_type = self.kwargs.get('category_type')
        category_slug = self.request.GET.get('category')
        
        if category_slug:
            try:
                category = ExpenseCategory.objects.get(slug=category_slug)
                context['selected_category'] = category
            except ExpenseCategory.DoesNotExist:
                pass
        
        if category_type:
            category_type_display = dict(ExpenseCategory.CategoryTypeChoices.choices).get(category_type, category_type)
            context['category_type'] = category_type
            context['category_type_display'] = category_type_display
        
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        
        category_slug = self.request.GET.get('category')
        if category_slug:
            try:
                category = ExpenseCategory.objects.get(slug=category_slug)
                kwargs['category'] = category
            except ExpenseCategory.DoesNotExist:
                pass
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, SUCCESS_MESSAGES['EXPENSE_CREATED'])
        return super().form_valid(form)


class ExpenseUpdateView(LoginRequiredMixin, UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expenses/expense_form.html'
    success_url = reverse_lazy('expenses:categories')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['category'] = self.object.category
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_category'] = self.object.category
        return context
    
    def form_valid(self, form):
        messages.success(self.request, SUCCESS_MESSAGES['EXPENSE_UPDATED'])
        return super().form_valid(form)


class ExpenseDeleteView(LoginRequiredMixin, DeleteView):
    model = Expense
    template_name = 'expenses/expense_confirm_delete.html'
    success_url = reverse_lazy('expenses:categories')
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, SUCCESS_MESSAGES['EXPENSE_DELETED'])
        return response


class ExpenseCategoryCreateView(LoginRequiredMixin, CreateView):
    model = ExpenseCategory
    form_class = ExpenseCategoryForm
    template_name = 'expenses/category_form.html'
    success_url = reverse_lazy('expenses:categories')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'New Expense Category'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, SUCCESS_MESSAGES['CATEGORY_CREATED'].format(name=form.instance.name))
        return super().form_valid(form)


class ExpenseCategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = ExpenseCategory
    form_class = ExpenseCategoryForm
    template_name = 'expenses/category_form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'category_slug'
    success_url = reverse_lazy('expenses:categories')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f'Edit Category: {self.object.name}'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, SUCCESS_MESSAGES['CATEGORY_UPDATED'].format(name=form.instance.name))
        return super().form_valid(form)


class ExpenseCategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = ExpenseCategory
    template_name = 'expenses/category_confirm_delete.html'
    slug_field = 'slug'
    slug_url_kwarg = 'category_slug'
    success_url = reverse_lazy('expenses:categories')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['expense_count'] = self.object.expenses.count()
        return context
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        expense_count = obj.expenses.count()
        
        if expense_count > 0:
            obj.expenses.all().delete()
            messages.warning(
                request, 
                f'{expense_count} expense(s) associated with category "{obj.name}" were deleted.'
            )
        
        messages.success(request, SUCCESS_MESSAGES['CATEGORY_DELETED'].format(name=obj.name))
        return super().delete(request, *args, **kwargs)
