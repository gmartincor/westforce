from django import template
from apps.accounting.constants import get_payment_icon

register = template.Library()


@register.filter
def payment_method_icon(payment_method):
    return get_payment_icon(payment_method)
