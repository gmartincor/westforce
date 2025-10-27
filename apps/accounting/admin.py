from django.contrib import admin
from django.utils.html import format_html
from .models import Income


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    
    list_display = [
        'service_type',
        'amount_display',
        'date',
        'payment_method',
        'client_name',
        'reference_number'
    ]
    
    list_filter = [
        'service_type',
        'payment_method',
        'date',
        'accounting_year',
        'accounting_month'
    ]
    
    search_fields = [
        'client_name',
        'reference_number',
        'description'
    ]
    
    date_hierarchy = 'date'
    
    ordering = ['-date', '-created']
    
    readonly_fields = ['accounting_year', 'accounting_month', 'created', 'modified']
    
    fieldsets = (
        ('Income Details', {
            'fields': ('service_type', 'amount', 'date', 'payment_method')
        }),
        ('Service Information', {
            'fields': ('client_name', 'pickup_address', 'delivery_address', 'description')
        }),
        ('Reference', {
            'fields': ('reference_number',)
        }),
        ('Accounting', {
            'fields': ('accounting_year', 'accounting_month'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )

    @admin.display(description='Amount', ordering='amount')
    def amount_display(self, obj):
        return format_html('<strong>${:.2f} AUD</strong>', obj.amount)
