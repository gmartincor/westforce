from django import template
from django.utils.safestring import mark_safe
from django.db.models import Sum, Count
from datetime import datetime
from apps.accounting.models import Income

register = template.Library()


@register.simple_tag
def currency_field(field):
    return mark_safe(str(field))


@register.simple_tag
def get_service_type_stats(service_type, year=None):
    queryset = Income.objects.filter(service_type=service_type)
    
    if year:
        queryset = queryset.filter(accounting_year=year)
    
    result = queryset.aggregate(
        total=Sum('amount'),
        count=Count('id')
    )
    
    return {
        'total': result['total'] or 0,
        'count': result['count'] or 0,
        'average': (result['total'] or 0) / max(result['count'] or 1, 1)
    }


@register.simple_tag
def total_income_by_year(year=None, month=None):
    queryset = Income.objects.all()
    
    if year:
        queryset = queryset.filter(accounting_year=year)
    if month:
        queryset = queryset.filter(accounting_month=month)
    
    return queryset.aggregate(total=Sum('amount'))['total'] or 0


@register.filter
def format_service_type(service_type):
    service_type_map = {
        'local': 'Local Move',
        'interstate': 'Interstate Move', 
        'international': 'International Move',
        'storage': 'Storage Service',
        'packing': 'Packing Service',
        'cleaning': 'Cleaning Service',
        'other': 'Other Service'
    }
    return service_type_map.get(service_type, service_type)


@register.filter
def format_payment_method(payment_method):
    method_map = {
        'CARD': 'Credit/Debit Card',
        'CASH': 'Cash',
        'BANK_TRANSFER': 'Bank Transfer',
        'EFTPOS': 'EFTPOS',
        'PAYPAL': 'PayPal',
        'CHEQUE': 'Cheque',
        'OTHER': 'Other'
    }
    return method_map.get(payment_method, payment_method)


@register.inclusion_tag('accounting/components/income_trend_chart.html')
def income_trend_chart(data, title="Income Trend"):
    return {
        'data': data,
        'title': title
    }


@register.simple_tag
def get_monthly_income_comparison(year, previous_year=None):
    if not previous_year:
        previous_year = year - 1
    
    current_year_data = []
    previous_year_data = []
    
    for month in range(1, 13):
        current = Income.objects.filter(
            accounting_year=year,
            accounting_month=month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        previous = Income.objects.filter(
            accounting_year=previous_year,
            accounting_month=month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        current_year_data.append(float(current))
        previous_year_data.append(float(previous))
    
    return {
        'current_year': {
            'year': year,
            'data': current_year_data
        },
        'previous_year': {
            'year': previous_year,
            'data': previous_year_data
        }
    }
