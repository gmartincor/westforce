from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory

from .models import Company, Invoice, InvoiceItem
from .constants import AUSTRALIAN_STATES
from .validators import AustralianBusinessValidator

FORM_CONTROL = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white'
CURRENCY_INPUT = 'w-full pl-8 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white'


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        exclude = ['current_number']
        widgets = {
            'legal_form': forms.Select(attrs={'class': FORM_CONTROL}),
            'business_name': forms.TextInput(attrs={'class': FORM_CONTROL, 'placeholder': 'Trading name'}),
            'legal_name': forms.TextInput(attrs={'class': FORM_CONTROL, 'placeholder': 'Registered legal name'}),
            'abn': forms.TextInput(attrs={'class': FORM_CONTROL, 'placeholder': 'XX XXX XXX XXX'}),
            'acn': forms.TextInput(attrs={'class': FORM_CONTROL, 'placeholder': 'XXX XXX XXX'}),
            'gst_registered': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded'}),
            'address': forms.Textarea(attrs={'rows': 2, 'class': FORM_CONTROL, 'placeholder': 'Street address'}),
            'postal_code': forms.TextInput(attrs={'class': FORM_CONTROL, 'placeholder': '1234'}),
            'city': forms.TextInput(attrs={'class': FORM_CONTROL, 'placeholder': 'Suburb'}),
            'state': forms.Select(attrs={'class': FORM_CONTROL}),
            'phone': forms.TextInput(attrs={'class': FORM_CONTROL, 'placeholder': '(02) 1234 5678'}),
            'email': forms.EmailInput(attrs={'class': FORM_CONTROL}),
            'website': forms.URLInput(attrs={'class': FORM_CONTROL, 'placeholder': 'https://'}),
            'bank_name': forms.TextInput(attrs={'class': FORM_CONTROL, 'placeholder': 'Bank name'}),
            'bsb': forms.TextInput(attrs={'class': FORM_CONTROL, 'placeholder': 'XXX-XXX'}),
            'account_number': forms.TextInput(attrs={'class': FORM_CONTROL, 'placeholder': 'Account number'}),
            'invoice_prefix': forms.TextInput(attrs={'class': FORM_CONTROL, 'placeholder': 'INV'}),
            'logo': forms.ClearableFileInput(attrs={'class': FORM_CONTROL}),
        }

    def clean_abn(self):
        abn = self.cleaned_data.get('abn', '')
        return AustralianBusinessValidator.validate_abn(abn)

    def clean_acn(self):
        acn = self.cleaned_data.get('acn', '')
        legal_form = self.cleaned_data.get('legal_form')
        
        if legal_form in ['PTY_LTD', 'PUBLIC_COMPANY'] and not acn:
            raise ValidationError('ACN is required for companies.')
        
        if acn:
            return AustralianBusinessValidator.validate_acn(acn)
        
        return acn


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['client_type', 'client_name', 'client_abn', 'client_address', 'issue_date', 'payment_terms', 'status', 'notes']
        widgets = {
            'client_type': forms.Select(attrs={'class': FORM_CONTROL}),
            'client_name': forms.TextInput(attrs={'class': FORM_CONTROL, 'placeholder': 'Client name'}),
            'client_abn': forms.TextInput(attrs={'class': FORM_CONTROL, 'placeholder': 'XX XXX XXX XXX'}),
            'client_address': forms.Textarea(attrs={'rows': 3, 'class': FORM_CONTROL, 'placeholder': 'Full address including postcode'}),
            'issue_date': forms.DateInput(attrs={'type': 'date', 'class': FORM_CONTROL}),
            'payment_terms': forms.Textarea(attrs={'rows': 2, 'class': FORM_CONTROL}),
            'status': forms.Select(attrs={'class': FORM_CONTROL}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': FORM_CONTROL, 'placeholder': 'Internal notes (optional)'}),
        }

    def clean_client_abn(self):
        client_type = self.cleaned_data.get('client_type')
        client_abn = self.cleaned_data.get('client_abn', '')
        
        if client_type == 'BUSINESS':
            if not client_abn:
                raise ValidationError('ABN is required for business clients.')
            return AustralianBusinessValidator.validate_abn(client_abn)
        
        return client_abn


class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['description', 'quantity', 'unit_price', 'gst_rate']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 2,
                'class': FORM_CONTROL,
                'placeholder': 'Service or product description'
            }),
            'quantity': forms.NumberInput(attrs={'class': FORM_CONTROL, 'min': '1', 'value': '1'}),
            'unit_price': forms.NumberInput(attrs={'step': '0.01', 'class': CURRENCY_INPUT, 'min': '0.01', 'placeholder': '0.00'}),
            'gst_rate': forms.Select(attrs={'class': FORM_CONTROL}),
        }


class BaseInvoiceItemFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance or not self.instance.pk or not self.instance.items.exists():
            self.extra = 1
        else:
            self.extra = 0
    
    def clean(self):
        if any(self.errors):
            return
        
        valid_forms = 0
        for form in self.forms:
            if form.cleaned_data.get('DELETE', False):
                continue
            if form.cleaned_data.get('description'):
                valid_forms += 1
        
        if valid_forms < 1:
            raise ValidationError('At least one line item is required.')


InvoiceItemFormSet = inlineformset_factory(
    Invoice,
    InvoiceItem,
    form=InvoiceItemForm,
    formset=BaseInvoiceItemFormSet,
    fields=['description', 'quantity', 'unit_price', 'gst_rate'],
    extra=0,
    min_num=0,
    validate_min=False,
    can_delete=True,
    max_num=50
)
