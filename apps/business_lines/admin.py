from django.contrib import admin
from django.utils.html import format_html
from .models import BusinessLine


@admin.register(BusinessLine)
class BusinessLineAdmin(admin.ModelAdmin):
    list_display = ['hierarchy_display', 'level', 'income_count_display', 'total_income_display', 'is_active']
    list_filter = ['level', 'is_active', 'parent']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['level', 'order', 'name']
    readonly_fields = ['level', 'created', 'modified']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Hierarchy', {
            'fields': ('parent', 'level', 'order')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created', 'modified'),
            'classes': ('collapse',)
        })
    )

    def hierarchy_display(self, obj):
        indent = "&nbsp;" * (obj.level - 1) * 4
        return format_html('{}{}', indent, obj.name)
    
    hierarchy_display.short_description = 'Business Line'

    def income_count_display(self, obj):
        try:
            count = obj.income_count
            return format_html('<strong>{}</strong>', count)
        except:
            return '0'
    
    income_count_display.short_description = 'Incomes'

    def total_income_display(self, obj):
        try:
            total = obj.total_income
            return format_html('<strong>${:.2f} AUD</strong>', total)
        except:
            return '$0.00 AUD'
    
    total_income_display.short_description = 'Total Income'
