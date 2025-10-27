from django import forms
from django.utils import timezone

from .models import Income


class IncomeFilterForm(forms.Form):
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
            'placeholder': 'From date'
        }),
        label='Date from'
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
            'placeholder': 'To date'
        }),
        label='Date to'
    )
    
    client_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
            'placeholder': 'Search by client name'
        }),
        label='Client name'
    )
    
    amount_min = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
            'step': '0.01',
            'min': '0',
            'placeholder': 'Min amount'
        }),
        label='Min amount'
    )
    
    amount_max = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm',
            'step': '0.01',
            'min': '0',
            'placeholder': 'Max amount'
        }),
        label='Max amount'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        amount_min = cleaned_data.get('amount_min')
        amount_max = cleaned_data.get('amount_max')
        
        if date_from and date_to and date_from > date_to:
            raise forms.ValidationError('Start date must be before or equal to end date.')
        
        if amount_min and amount_max and amount_min > amount_max:
            raise forms.ValidationError('Minimum amount must be less than or equal to maximum amount.')
        
        return cleaned_data
