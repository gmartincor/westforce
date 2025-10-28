PAYMENT_METHOD_ICONS = {
    'CARD': 'credit-card',
    'CASH': 'money-bill-wave',
    'BANK_TRANSFER': 'university',
    'EFTPOS': 'credit-card',
    'PAYPAL': 'paypal',
    'CHEQUE': 'money-check',
    'OTHER': 'coins'
}


def get_payment_icon(payment_method: str) -> str:
    return PAYMENT_METHOD_ICONS.get(payment_method, 'coins')
