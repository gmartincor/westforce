from django import forms
from django.utils import timezone
from .models import Expense, ExpenseCategory
from apps.core.form_utils import apply_currency_field_styles


class ExpenseCategoryForm(forms.ModelForm):
    
    class Meta:
        model = ExpenseCategory
        fields = ['name', 'category_type', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500'
            }),
            'category_type': forms.Select(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500'
            }),
            'description': forms.Textarea(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
                'rows': 3,
                'placeholder': 'Optional'
            }),
        }


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['description', 'amount', 'date', 'category', 'invoice_number']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
                'rows': 3
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'date': forms.DateInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
                'type': 'date'
            }),
            'category': forms.Select(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500'
            }),
            'invoice_number': forms.TextInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
                'placeholder': 'Optional'
            }),
        }

    def __init__(self, *args, category=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if not self.instance.pk and not self.initial.get('date'):
            self.initial['date'] = timezone.now().date()
        
        self.fields['category'].queryset = ExpenseCategory.objects.filter(
            is_active=True
        ).order_by('category_type', 'name')
        
        apply_currency_field_styles(self.fields['amount'])
        
        if category:
            self.fields['category'].widget = forms.HiddenInput()
            self.initial['category'] = category

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.accounting_year = instance.date.year
            instance.accounting_month = instance.date.month
            instance.save()
        return instance
