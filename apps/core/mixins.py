from django.utils import timezone
from django.http import Http404, JsonResponse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from typing import Dict, Any, Optional


class WestforceLoginRequiredMixin(LoginRequiredMixin):
    login_url = reverse_lazy('authentication:login')


class WestforceContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'app_name': 'Westforce',
            'company_type': 'Moving Company',
        })
        return context


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


class BusinessLineHierarchyMixin:
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
