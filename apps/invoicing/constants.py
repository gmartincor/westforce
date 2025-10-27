from decimal import Decimal


GST_RATE = Decimal('10.00')
GST_FREE_RATE = Decimal('0.00')
TAX_INVOICE_THRESHOLD = Decimal('82.50')
RECORD_RETENTION_YEARS = 5


LEGAL_FORMS = [
    ('SOLE_TRADER', 'Sole Trader'),
    ('PTY_LTD', 'Proprietary Limited Company (Pty Ltd)'),
    ('PUBLIC_COMPANY', 'Public Company Limited'),
    ('PARTNERSHIP', 'Partnership'),
    ('TRUST', 'Trust'),
]


CLIENT_TYPES = [
    ('BUSINESS', 'Business (ABN holder)'),
    ('INDIVIDUAL', 'Individual'),
]


INVOICE_STATUS = [
    ('DRAFT', 'Draft'),
    ('SENT', 'Sent'),
    ('PAID', 'Paid'),
    ('OVERDUE', 'Overdue'),
    ('CANCELLED', 'Cancelled'),
]


GST_TREATMENT = [
    ('TAXABLE', 'Taxable (10% GST)'),
    ('GST_FREE', 'GST-free (health, education, exports)'),
    ('INPUT_TAXED', 'Input taxed (financial supplies, residential rent)'),
]


GST_RATE_CHOICES = [
    (GST_RATE, '10% (Standard GST)'),
    (GST_FREE_RATE, '0% (GST-free)'),
]


PAYMENT_TERMS_TEMPLATES = [
    'Payment due within 7 days',
    'Payment due within 14 days',
    'Payment due within 30 days',
    'Payment due on receipt',
    'Payment due end of month',
]


AUSTRALIAN_STATES = [
    ('NSW', 'New South Wales'),
    ('VIC', 'Victoria'),
    ('QLD', 'Queensland'),
    ('WA', 'Western Australia'),
    ('SA', 'South Australia'),
    ('TAS', 'Tasmania'),
    ('ACT', 'Australian Capital Territory'),
    ('NT', 'Northern Territory'),
]
