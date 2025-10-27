from django.contrib import admin
from .models import Company, Invoice, InvoiceItem


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    min_num = 1
    fields = ['description', 'quantity', 'unit_price', 'gst_rate']


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'legal_form', 'abn', 'gst_registered', 'city', 'state']
    list_filter = ['legal_form', 'gst_registered', 'state']
    search_fields = ['business_name', 'abn', 'acn']
    readonly_fields = ['current_number']
    fieldsets = (
        ('Business Information', {
            'fields': ('legal_form', 'business_name', 'legal_name', 'abn', 'acn', 'gst_registered')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'postal_code')
        }),
        ('Contact', {
            'fields': ('phone', 'email', 'website')
        }),
        ('Banking Details', {
            'fields': ('bank_name', 'bsb', 'account_number')
        }),
        ('Invoice Configuration', {
            'fields': ('invoice_prefix', 'current_number', 'logo')
        }),
    )


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['reference', 'client_name', 'issue_date', 'total_amount', 'status']
    list_filter = ['status', 'client_type', 'issue_date']
    search_fields = ['reference', 'client_name', 'client_abn']
    readonly_fields = ['reference', 'subtotal', 'gst_amount', 'total_amount', 'is_tax_invoice']
    date_hierarchy = 'issue_date'
    inlines = [InvoiceItemInline]
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('reference', 'issue_date', 'status')
        }),
        ('Client Details', {
            'fields': ('client_type', 'client_name', 'client_abn', 'client_address')
        }),
        ('Payment Terms', {
            'fields': ('payment_terms', 'notes')
        }),
        ('Totals', {
            'fields': ('subtotal', 'gst_amount', 'total_amount', 'is_tax_invoice'),
            'classes': ('collapse',)
        }),
        ('PDF File', {
            'fields': ('pdf_file',)
        }),
    )


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'description', 'quantity', 'unit_price', 'gst_rate', 'total']
    search_fields = ['invoice__reference', 'description']
    
    def total(self, obj):
        return f"${obj.total:.2f}"
    total.short_description = 'Total'
