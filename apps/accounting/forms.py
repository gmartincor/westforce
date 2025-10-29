from django import forms
from .models import Income, ServiceTypeChoices


TAILWIND_INPUT_CLASSES = 'block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm'


class DateRangeFilterMixin:
    
    def add_date_range_fields(self):
        self.fields['date_from'] = forms.DateField(
            required=False,
            widget=forms.DateInput(attrs={'type': 'date', 'class': TAILWIND_INPUT_CLASSES}),
            label='From'
        )
        
        self.fields['date_to'] = forms.DateField(
            required=False,
            widget=forms.DateInput(attrs={'type': 'date', 'class': TAILWIND_INPUT_CLASSES}),
            label='To'
        )
    
    def validate_date_range(self, cleaned_data):
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise forms.ValidationError('Start date must be before or equal to end date.')
        
        return cleaned_data


class IncomeFilterForm(forms.Form, DateRangeFilterMixin):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_date_range_fields()
    
    client_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASSES, 'placeholder': 'Search by client name'}),
        label='Client name'
    )
    
    amount_min = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': TAILWIND_INPUT_CLASSES, 'step': '0.01', 'min': '0', 'placeholder': 'Min amount'}),
        label='Min amount'
    )
    
    amount_max = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': TAILWIND_INPUT_CLASSES, 'step': '0.01', 'min': '0', 'placeholder': 'Max amount'}),
        label='Max amount'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        cleaned_data = self.validate_date_range(cleaned_data)
        
        amount_min = cleaned_data.get('amount_min')
        amount_max = cleaned_data.get('amount_max')
        
        if amount_min and amount_max and amount_min > amount_max:
            raise forms.ValidationError('Minimum amount must be less than or equal to maximum amount.')
        
        return cleaned_data


class ProfitFilterForm(forms.Form, DateRangeFilterMixin):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_date_range_fields()
        self.add_service_type_fields()
        self.add_expense_category_fields()
    
    def add_service_type_fields(self):
        self.fields['service_types'] = forms.MultipleChoiceField(
            required=False,
            choices=ServiceTypeChoices.choices,
            widget=forms.CheckboxSelectMultiple(attrs={'class': 'mr-2'}),
            label='Service Types'
        )
    
    def add_expense_category_fields(self):
        from apps.expenses.models import ExpenseCategory
        
        self.fields['expense_categories'] = forms.MultipleChoiceField(
            required=False,
            choices=ExpenseCategory.CategoryTypeChoices.choices,
            widget=forms.CheckboxSelectMultiple(attrs={'class': 'mr-2'}),
            label='Expense Categories'
        )
    
    def clean(self):
        cleaned_data = super().clean()
        return self.validate_date_range(cleaned_data)
