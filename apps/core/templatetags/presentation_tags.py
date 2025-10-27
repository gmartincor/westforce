from django import template
from django.utils.safestring import mark_safe
from decimal import Decimal

register = template.Library()


@register.filter
def format_currency(value, symbol="$"):
    if value is None:
        return f"{symbol}0.00"
    
    try:
        amount = Decimal(str(value))
        return f"{symbol}{amount:,.2f}"
    except (ValueError, TypeError):
        return f"{symbol}0.00"


@register.simple_tag
def percentage_of(part, total):
    if not total or total == 0:
        return "0"
    
    try:
        percentage = (Decimal(str(part)) / Decimal(str(total))) * 100
        return f"{percentage:.1f}"
    except (ValueError, TypeError, ZeroDivisionError):
        return "0"


@register.filter
def abs_value(value):
    try:
        return abs(Decimal(str(value)))
    except (ValueError, TypeError):
        return 0


@register.filter
def multiply(value, arg):
    try:
        return Decimal(str(value)) * Decimal(str(arg))
    except (ValueError, TypeError):
        return 0


@register.filter
def divide(value, arg):
    try:
        if arg == 0:
            return 0
        return Decimal(str(value)) / Decimal(str(arg))
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.filter 
def div(value, arg):
    return divide(value, arg)


@register.simple_tag
def progress_bar(current, total, color="blue"):
    if not total or total == 0:
        percentage = 0
    else:
        percentage = min(100, (current / total) * 100)
    
    return mark_safe(f'''
        <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div class="bg-{color}-500 h-2 rounded-full" style="width: {percentage}%"></div>
        </div>
    ''')


@register.inclusion_tag('accounting/components/amount_badge.html')
def amount_badge(amount, type="default"):
    color_classes = {
        'income': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
        'expense': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
        'profit': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
        'default': 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
    }
    
    return {
        'amount': amount,
        'color_class': color_classes.get(type, color_classes['default'])
    }
