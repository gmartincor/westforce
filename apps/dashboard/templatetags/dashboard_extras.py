from django import template
from django.utils.safestring import mark_safe
import json

register = template.Library()


@register.filter
def json_encode(value):
    return mark_safe(json.dumps(value))


@register.filter
def format_currency(value):
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return "$0.00"


@register.filter
def positive_class(value):
    try:
        return 'text-green-600 dark:text-green-400' if float(value) >= 0 else 'text-red-600 dark:text-red-400'
    except (ValueError, TypeError):
        return 'text-gray-600 dark:text-gray-400'


@register.filter
def positive_bg_class(value):
    try:
        return 'bg-green-100 dark:bg-green-900' if float(value) >= 0 else 'bg-red-100 dark:bg-red-900'
    except (ValueError, TypeError):
        return 'bg-gray-100 dark:bg-gray-900'
