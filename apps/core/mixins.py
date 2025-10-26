from django.utils import timezone
from django.http import Http404
from django.core.exceptions import PermissionDenied


class TemporalFilterMixin:
    def get_temporal_filters(self):
        year = self.request.GET.get('year')
        month = self.request.GET.get('month')
        
        current_date = timezone.now()
        
        if year:
            try:
                year = int(year)
            except (ValueError, TypeError):
                year = current_date.year
        else:
            year = current_date.year
        
        if month:
            try:
                month = int(month)
                if month < 1 or month > 12:
                    month = current_date.month
            except (ValueError, TypeError):
                month = current_date.month
        else:
            month = current_date.month
        
        return {'year': year, 'month': month}
    
    def get_temporal_context(self):
        filters = self.get_temporal_filters()
        return {
            'selected_year': filters['year'],
            'selected_month': filters['month'],
            'current_year': timezone.now().year,
            'current_month': timezone.now().month,
        }
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_temporal_context())
        return context


class BusinessLinePermissionMixin:
    def get_allowed_business_lines(self):
        from apps.business_lines.models import BusinessLine
        return BusinessLine.objects.select_related('parent').all()
    
    def filter_business_lines_by_permission(self, queryset):
        return queryset
    
    def check_business_line_permission(self, business_line):
        return True
    
    def enforce_business_line_permission(self, business_line):
        pass


class CategoryNormalizationMixin:
    @staticmethod
    def normalize_category_for_url(category):
        return category.lower() if category else None
    
    @staticmethod
    def normalize_category_for_comparison(category):
        return category.lower() if category else None


class BusinessLineHierarchyMixin(CategoryNormalizationMixin):
    def resolve_business_line_from_path(self, line_path):
        from apps.business_lines.models import BusinessLine
        
        if not line_path:
            raise Http404("Business line path not specified.")
        
        path_parts = line_path.strip('/').split('/')
        
        if len(path_parts) == 1:
            try:
                return BusinessLine.objects.select_related('parent').get(
                    slug=path_parts[0], 
                    level=1
                )
            except BusinessLine.DoesNotExist:
                raise Http404(f"Business line '{path_parts[0]}' not found.")
            except BusinessLine.MultipleObjectsReturned:
                raise Http404(f"Multiple business lines found with slug '{path_parts[0]}'. Contact the administrator.")
        
        current_line = None
        for i, slug in enumerate(path_parts):
            try:
                if i == 0:
                    current_line = BusinessLine.objects.select_related('parent').get(
                        slug=slug, level=1
                    )
                else:
                    current_line = BusinessLine.objects.select_related('parent').get(
                        slug=slug, 
                        parent=current_line,
                        level=i + 1
                    )
            except BusinessLine.DoesNotExist:
                raise Http404(f"Business line '{slug}' not found at level {i + 1}.")
            except BusinessLine.MultipleObjectsReturned:
                raise Http404(f"Multiple business lines found with slug '{slug}' at level {i + 1}. Contact the administrator.")
        
        return current_line
    
    def get_hierarchy_path(self, business_line):
        if not business_line:
            return []
        
        path = []
        current = business_line
        
        while current:
            path.insert(0, current)
            current = current.parent
        return path
    
    def get_breadcrumb_path(self, business_line, category=None):
        """Build breadcrumb path for business line navigation"""
        breadcrumbs = []
        hierarchy = self.get_hierarchy_path(business_line)
        
        for line in hierarchy:
            breadcrumbs.append({
                'name': line.name,
                'url': f'/accounting/{line.get_url_path()}/',
                'is_active': line == business_line
            })
        
        if category:
            breadcrumbs.append({
                'name': category.title(),
                'url': f'/accounting/{business_line.get_url_path()}/{category}/',
                'is_active': True
            })
        
        return breadcrumbs
    
    def get_business_line_context(self, line_path=None, category=None):
        context = {}
        
        if line_path:
            business_line = self.resolve_business_line_from_path(line_path)
            
            if hasattr(self, 'check_business_line_permission'):
                if not self.check_business_line_permission(business_line):
                    return {
                        'business_line': business_line,
                        'line_path': line_path,
                        'has_permission': False
                    }
            
            context.update({
                'business_line': business_line,
                'hierarchy_path': self.get_hierarchy_path(business_line),
                'breadcrumb_path': self.get_breadcrumb_path(business_line, category),
                'current_category': self.normalize_category_for_url(category),
                'line_path': line_path,
                'has_permission': True
            })
        
        return context


class ServiceCategoryMixin(CategoryNormalizationMixin):
    
    def get_business_line_incomes(self, business_line):
        from apps.accounting.models import Income
        
        descendant_ids = business_line.get_descendant_ids()
        return Income.objects.filter(business_line__id__in=descendant_ids)
    
    def get_business_line_stats(self, business_line):
        from django.db.models import Sum, Count, Avg
        
        incomes = self.get_business_line_incomes(business_line)
        
        stats = incomes.aggregate(
            total_revenue=Sum('amount'),
            income_count=Count('id'),
            avg_revenue=Avg('amount')
        )
        
        return {
            'total_revenue': stats['total_revenue'] or 0,
            'income_count': stats['income_count'] or 0,
            'avg_revenue': stats['avg_revenue'] or 0,
        }
    
    def get_service_type_breakdown(self, business_line):
        from django.db.models import Sum, Count
        from apps.accounting.models import ServiceTypeChoices
        
        incomes = self.get_business_line_incomes(business_line)
        breakdown = {}
        
        for service_type, display_name in ServiceTypeChoices.choices:
            type_stats = incomes.filter(service_type=service_type).aggregate(
                total=Sum('amount'),
                count=Count('id')
            )
            breakdown[service_type] = {
                'name': display_name,
                'total': type_stats['total'] or 0,
                'count': type_stats['count'] or 0
            }
        
        return breakdown
    
    def get_business_line_context(self, business_line):
        stats = self.get_business_line_stats(business_line)
        breakdown = self.get_service_type_breakdown(business_line)
        
        return {
            'business_line_stats': stats,
            'service_type_breakdown': breakdown,
        }
