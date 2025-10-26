from django.contrib import admin
from .models import Company, Invoice, InvoiceItem


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    min_num = 1
    fields = ['description', 'quantity', 'unit_price', 'gst_rate', 'withholding_rate']


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'legal_form', 'tax_id', 'city']
    list_filter = ['legal_form']
    search_fields = ['business_name', 'tax_id']
    readonly_fields = ['current_number']
    fieldsets = (
        ('Información básica', {
            'fields': ('legal_form', 'business_name', 'legal_name', 'tax_id')
        }),
        ('Dirección', {
            'fields': ('address', 'postal_code', 'city', 'province')
        }),
        ('Contacto', {
            'fields': ('phone', 'email')
        }),
        ('Datos bancarios', {
            'fields': ('bank_name', 'iban')
        }),
        ('Información legal', {
            'fields': ('mercantile_registry', 'share_capital')
        }),
        ('Configuración de facturas', {
            'fields': ('invoice_prefix', 'current_number', 'logo')
        }),
    )


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['reference', 'client_name', 'issue_date', 'total_amount', 'status']
    list_filter = ['status', 'client_type', 'issue_date']
    search_fields = ['reference', 'client_name', 'client_tax_id']
    readonly_fields = ['reference', 'base_amount', 'gst_amount', 'withholding_amount', 'total_amount']
    date_hierarchy = 'issue_date'
    inlines = [InvoiceItemInline]
    
    fieldsets = (
        ('Información de la factura', {
            'fields': ('reference', 'issue_date', 'status')
        }),
        ('Cliente', {
            'fields': ('client_type', 'client_name', 'client_tax_id', 'client_address')
        }),
        ('Condiciones de pago', {
            'fields': ('payment_terms',)
        }),
        ('Totals', {
            'fields': ('base_amount', 'gst_amount', 'withholding_amount', 'total_amount'),
            'classes': ('collapse',)
        }),
        ('Archivo PDF', {
            'fields': ('pdf_file',)
        }),
    )


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'description', 'quantity', 'unit_price', 'gst_rate', 'withholding_rate']
    search_fields = ['invoice__reference', 'description']
