from django.contrib import admin
from django.utils.html import format_html
from .models import Income, ServiceTypeChoices, PaymentMethodChoices


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    
    list_display = [
        'business_line',
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
        'business_line',
        'date',
        'accounting_year',
        'accounting_month'
    ]
    
    search_fields = [
        'client_name',
        'business_line__name',
        'reference_number',
        'description'
    ]
    
    date_hierarchy = 'date'
    
    ordering = ['-date', '-created']
    
    readonly_fields = ['accounting_year', 'accounting_month', 'created', 'modified']
    
    fieldsets = (
        ('Income Details', {
            'fields': ('business_line', 'service_type', 'amount', 'date', 'payment_method')
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

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('business_line')
