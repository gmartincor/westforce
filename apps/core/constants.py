MONTHS_DICT = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April',
    5: 'May', 6: 'June', 7: 'July', 8: 'August',
    9: 'September', 10: 'October', 11: 'November', 12: 'December'
}

MONTHS_CHOICES = [
    (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
    (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
    (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
]

DEFAULT_START_YEAR = 2024
FINANCIAL_YEAR_BUFFER = 3

DEFAULT_PAGINATION = 25

SUCCESS_MESSAGES = {
    'CATEGORY_CREATED': 'Category "{name}" created successfully.',
    'CATEGORY_UPDATED': 'Category "{name}" updated successfully.',
    'CATEGORY_DELETED': 'Category "{name}" deleted successfully.',
    'EXPENSE_CREATED': 'Expense recorded successfully.',
    'EXPENSE_UPDATED': 'Expense updated successfully.',
    'EXPENSE_DELETED': 'Expense deleted successfully.',
}

ERROR_MESSAGES = {
    'CATEGORY_HAS_EXPENSES': (
        'Cannot delete category "{name}" because it has associated expenses. '
        'Please reassign or delete all expenses in this category first.'
    ),
    'INVALID_CATEGORY_TYPE': 'Invalid category type',
}

ACCOUNTING_SUCCESS_MESSAGES = {
    'CLIENT_CREATED': 'Customer "{name}" created successfully.',
    'CLIENT_UPDATED': 'Customer "{name}" updated successfully.',
    'CLIENT_DELETED': 'Customer "{name}" deleted successfully.',
    'SERVICE_CREATED': 'Moving service for "{client}" created successfully.',
    'SERVICE_UPDATED': 'Moving service updated successfully.',
    'SERVICE_DELETED': 'Moving service deleted successfully.',
    'BALANCE_UPDATED': 'Balance updated successfully.',
}

ACCOUNTING_ERROR_MESSAGES = {
    'INVALID_BUSINESS_LINE_PATH': 'Business line path "{path}" is not valid.',
    'BUSINESS_LINE_NOT_FOUND': 'Business line "{name}" not found.',
    'PERMISSION_DENIED_BUSINESS_LINE': 'You do not have permission to access business line "{name}".',
    'INVALID_SERVICE_CATEGORY': 'Service category "{category}" is not valid. Must be RESIDENTIAL or COMMERCIAL.',
    'BALANCE_NOT_ALLOWED': 'Balances are not allowed for business line "{name}".',
    'INVALID_BALANCE_FIELD': 'Balance field "{field}" is not valid for business line "{name}".',
    'CLIENT_HAS_ACTIVE_SERVICES': (
        'Cannot delete customer "{name}" because they have active moving services. '
        'Please deactivate or delete all associated services first.'
    ),
    'DUPLICATE_SERVICE': 'A "{category}" moving service already exists for this customer in this business line.',
}

ACCOUNTING_URL_PATTERNS = {
    'INDEX': 'accounting:index',
    'LINE_DETAIL': 'accounting:business-lines-path',
    'RESIDENTIAL_SERVICES': 'accounting:residential-services',
    'COMMERCIAL_SERVICES': 'accounting:commercial-services',
    'SERVICE_CREATE': 'accounting:service-create',
    'SERVICE_EDIT': 'accounting:service-edit',
    'SERVICE_DELETE': 'accounting:service-delete',
    'CLIENT_CREATE': 'accounting:client-create',
    'CLIENT_EDIT': 'accounting:client-edit',
}

SERVICE_CATEGORIES = {
    'RESIDENTIAL': 'residential',
    'COMMERCIAL': 'commercial',
}

SERVICE_CATEGORY_DISPLAY = {
    'RESIDENTIAL': 'Residential Moving',
    'COMMERCIAL': 'Commercial Moving',
}

EXPENSE_SERVICE_CATEGORIES = {
    'RESIDENTIAL': 'residential',
    'COMMERCIAL': 'commercial',
    'SHARED': 'shared',
}

EXPENSE_SERVICE_CATEGORY_DISPLAY = {
    'RESIDENTIAL': 'Residential',
    'COMMERCIAL': 'Commercial',
    'SHARED': 'Shared',
}

PAYMENT_METHOD_DISPLAY = {
    'CARD': 'Credit/Debit Card',
    'CASH': 'Cash',
    'TRANSFER': 'Bank Transfer',
    'EFTPOS': 'EFTPOS',
    'PAYPAL': 'PayPal',
    'CHEQUE': 'Cheque',
}

GENDER_DISPLAY = {
    'M': 'Male',
    'F': 'Female',
    'O': 'Other',
}

BUSINESS_LINE_LEVELS = {
    'LEVEL_1': 1,
    'LEVEL_2': 2,
    'LEVEL_3': 3,
}

NAVIGATION_ITEMS = {
    'ACCOUNTING': {
        'name': 'Revenue',
        'icon': 'currency-dollar',
        'subitems': [
            {'name': 'By Business Line', 'url': 'accounting:index'},
            {'name': 'By Category', 'url': 'accounting:by-category'},
            {'name': 'By Customer', 'url': 'accounting:by-client'},
        ]
    }
}

CATEGORY_CONFIG = {
    'residential': {
        'name': 'Residential Moving',
        'color': 'green',
        'icon': 'check-circle',
        'badge_class': 'bg-blue-100 text-blue-800',
        'bg_class': 'bg-emerald-100 dark:bg-emerald-900',
        'text_class': 'text-emerald-600 dark:text-emerald-300'
    },
    'commercial': {
        'name': 'Commercial Moving',
        'color': 'purple',
        'icon': 'exclamation-circle',
        'badge_class': 'bg-gray-100 text-gray-800',
        'bg_class': 'bg-purple-100 dark:bg-purple-900',
        'text_class': 'text-purple-600 dark:text-purple-300'
    }
}

CATEGORY_DEFAULTS = {
    'DEFAULT_CATEGORY': 'residential',
    'VALID_CATEGORIES': ['residential', 'commercial']
}

APP_SUCCESS_MESSAGES = {
    'USER_CREATED': 'User "{name}" created successfully.',
    'USER_UPDATED': 'User "{name}" updated successfully.',
    'USER_ACTIVATED': 'User "{name}" activated successfully.',
    'USER_DEACTIVATED': 'User "{name}" deactivated successfully.',
    'USER_DELETED': 'User "{name}" deleted successfully.',
}

APP_ERROR_MESSAGES = {
    'EMAIL_EXISTS': 'An account with email "{email}" already exists.',
    'USER_NOT_FOUND': 'User not found.',
    'USER_INACTIVE': 'Account is deactivated.',
    'USER_SUSPENDED': 'Account is suspended.',
}
