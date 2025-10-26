from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.http import Http404
from django.core.exceptions import FieldError
from django.db import connection

from apps.expenses.models import Expense, ExpenseCategory
from apps.expenses.forms import ExpenseForm, ExpenseCategoryForm
from apps.core.mixins import TemporalFilterMixin
from apps.core.constants import SUCCESS_MESSAGES, ERROR_MESSAGES
from apps.core.services.temporal_service import parse_temporal_filters, get_temporal_context


class ExpenseCategoryView(LoginRequiredMixin, TemplateView):
    template_name = 'expenses/categories.html'
    
    def get(self, request, *args, **kwargs):
        service_category = kwargs.get('service_category')
        if not service_category:
            return redirect('expenses:categories', service_category='business')
        
        if service_category not in ['personal', 'business']:
            service_category = 'business'
        
        context = self.get_context_data(service_category=service_category)
        return self.render_to_response(context)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service_category = kwargs.get('service_category', 'business')
        
        filters = parse_temporal_filters(self.request)
        expense_filter = filters['expense_filter']
        year = filters['year']
        month = filters['month']
        
        if self._has_service_category_column():
            expense_filter['service_category'] = service_category
        
        category_totals = {}
        for category_type, display_name in ExpenseCategory.CategoryTypeChoices.choices:
            try:
                total = Expense.objects.filter(
                    category__category_type=category_type,
                    **expense_filter
                ).aggregate(total=Sum('amount'))['total'] or 0
            except FieldError:
                basic_filter = {k: v for k, v in expense_filter.items() if k != 'service_category'}
                total = Expense.objects.filter(
                    category__category_type=category_type,
                    **basic_filter
                ).aggregate(total=Sum('amount'))['total'] or 0
            
            category_totals[category_type] = {
                'name': display_name,
                'total': total,
            }
        
        total_general = sum(total['total'] for total in category_totals.values())
        
        base_filter = Q(expenses__accounting_year=year)
        if month:
            base_filter &= Q(expenses__accounting_month=month)
        if self._has_service_category_column():
            try:
                base_filter &= Q(expenses__service_category=service_category)
            except FieldError:
                pass
        
        categories = ExpenseCategory.objects.filter(
            is_active=True
        ).annotate(
            total_amount=Sum('expenses__amount', filter=base_filter),
            expense_count=Count('expenses', filter=base_filter)
        ).order_by('category_type', 'name')
        
        context.update({
            'service_category': service_category,
            'service_category_display': 'Personal' if service_category == 'personal' else 'Business',
            'category_totals': category_totals,
            'total_general': total_general,
            'categories': categories,
            'has_service_category': self._has_service_category_column(),
            **get_temporal_context(year, month)
        })
        
        return context
    
    def _has_service_category_column(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'expenses' 
                    AND column_name = 'service_category'
                """)
                return cursor.fetchone() is not None
        except Exception:
            return False


class ExpenseListView(LoginRequiredMixin, TemporalFilterMixin, ListView):
    model = Expense
    template_name = 'expenses/expense_list.html'
    context_object_name = 'expenses'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        service_category = self.kwargs.get('service_category')
        category_type = self.kwargs.get('category_type')
        category_slug = self.kwargs.get('category_slug')
        
        if category_slug:
            category = get_object_or_404(ExpenseCategory, slug=category_slug)
            queryset = queryset.filter(category=category)
            self.category = category
        elif category_type:
            queryset = queryset.filter(category__category_type=category_type)
        
        if service_category and self._has_service_category_column():
            try:
                queryset = queryset.filter(service_category=service_category)
            except FieldError:
                pass
        
        filters = parse_temporal_filters(self.request)
        expense_filter = filters['expense_filter']
        queryset = queryset.filter(**expense_filter)
        
        return queryset.select_related('category').order_by('-date', '-created')
    
    def _has_service_category_column(self):
        """Verificar si la columna service_category existe en la tabla expenses"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'expenses' 
                    AND column_name = 'service_category'
                """)
                return cursor.fetchone() is not None
        except Exception:
            return False
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        service_category = self.kwargs.get('service_category', 'business')
        category_type = self.kwargs.get('category_type')
        category_slug = self.kwargs.get('category_slug')
        
        filters = parse_temporal_filters(self.request)
        year = filters['year']
        month = filters['month']
        
        context.update({
            'service_category': service_category,
            'service_category_display': 'Personal' if service_category == 'personal' else 'Business',
            'category_type': category_type,
            'category_slug': category_slug,
            'has_service_category': self._has_service_category_column(),
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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        service_category = self.kwargs.get('service_category', 'personal')
        category_type = self.kwargs.get('category_type')
        
        context['service_category'] = service_category
        context['service_category_display'] = 'Personal' if service_category == 'personal' else 'Business'
        
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
    
    def get_initial(self):
        initial = super().get_initial()
        service_category = self.kwargs.get('service_category', 'personal')
        initial['service_category'] = service_category
        return initial
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        service_category = self.kwargs.get('service_category', 'personal')
        kwargs['service_category'] = service_category
        
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
    
    def get_success_url(self):
        service_category = self.kwargs.get('service_category', 'personal')
        category_type = self.kwargs.get('category_type')
        
        if category_type:
            return reverse_lazy('expenses:by-type', kwargs={
                'service_category': service_category,
                'category_type': category_type
            })
        return reverse_lazy('expenses:categories', kwargs={'service_category': service_category})


class ExpenseUpdateView(LoginRequiredMixin, UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expenses/expense_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['category'] = self.object.category
        kwargs['service_category'] = self.object.service_category
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service_category'] = self.object.service_category
        context['service_category_display'] = 'Personal' if self.object.service_category == 'personal' else 'Business'
        context['selected_category'] = self.object.category
        return context
    
    def form_valid(self, form):
        messages.success(self.request, SUCCESS_MESSAGES['EXPENSE_UPDATED'])
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('expenses:categories', kwargs={
            'service_category': self.object.service_category
        })


class ExpenseDeleteView(LoginRequiredMixin, DeleteView):
    model = Expense
    template_name = 'expenses/expense_confirm_delete.html'
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, SUCCESS_MESSAGES['EXPENSE_DELETED'])
        return response
    
    def get_success_url(self):
        return reverse_lazy('expenses:categories', kwargs={
            'service_category': self.object.service_category
        })


class ExpenseCategoryCreateView(LoginRequiredMixin, CreateView):
    model = ExpenseCategory
    form_class = ExpenseCategoryForm
    template_name = 'expenses/category_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        service_category = self.request.GET.get('service_category', 'business')
        kwargs['service_category'] = service_category
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service_category = self.request.GET.get('service_category', 'business')
        service_category_display = 'Personal' if service_category == 'personal' else 'Business'
        context['form_title'] = f'Nueva Categoría {service_category_display}'
        context['service_category'] = service_category
        context['service_category_display'] = service_category_display
        return context
    
    def form_valid(self, form):
        messages.success(self.request, SUCCESS_MESSAGES['CATEGORY_CREATED'].format(name=form.instance.name))
        return super().form_valid(form)
    
    def get_success_url(self):
        service_category = self.request.GET.get('service_category', 'personal')
        return reverse_lazy('expenses:categories', kwargs={'service_category': service_category})


class ExpenseCategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = ExpenseCategory
    form_class = ExpenseCategoryForm
    template_name = 'expenses/category_form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'category_slug'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        service_category = self.request.GET.get('service_category')
        if not service_category:
            most_common = self.object.expenses.values('service_category').annotate(
                count=Count('id')
            ).order_by('-count').first()
            service_category = most_common['service_category'] if most_common else 'business'
        kwargs['service_category'] = service_category
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service_category = self.request.GET.get('service_category')
        if not service_category:
            most_common = self.object.expenses.values('service_category').annotate(
                count=Count('id')
            ).order_by('-count').first()
            service_category = most_common['service_category'] if most_common else 'business'
        service_category_display = 'Personal' if service_category == 'personal' else 'Business'
        context['form_title'] = f'Editar Categoría {service_category_display}'
        context['service_category'] = service_category
        context['service_category_display'] = service_category_display
        return context
    
    def form_valid(self, form):
        messages.success(self.request, SUCCESS_MESSAGES['CATEGORY_UPDATED'].format(name=form.instance.name))
        return super().form_valid(form)
    
    def get_success_url(self):
        service_category = self.request.GET.get('service_category', 'personal')
        return reverse_lazy('expenses:categories', kwargs={'service_category': service_category})


class ExpenseCategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = ExpenseCategory
    template_name = 'expenses/category_confirm_delete.html'
    slug_field = 'slug'
    slug_url_kwarg = 'category_slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['expense_count'] = self.object.expenses.count()
        context['service_category'] = self.request.GET.get('service_category', 'business')
        return context
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        expense_count = obj.expenses.count()
        
        if expense_count > 0:
            obj.expenses.all().delete()
            messages.warning(
                request, 
                f'Se eliminaron {expense_count} gasto(s) asociado(s) a la categoría "{obj.name}".'
            )
        
        messages.success(request, SUCCESS_MESSAGES['CATEGORY_DELETED'].format(name=obj.name))
        return super().delete(request, *args, **kwargs)
    
    def get_success_url(self):
        service_category = self.request.GET.get('service_category', 'business')
        return reverse_lazy('expenses:categories', kwargs={'service_category': service_category})
