from django.db.models import Sum, Count, Avg
from typing import List, Dict
from apps.accounting.models import Income, ServiceTypeChoices
from .base import BaseAnalyticsService, BaseAggregationService


class ServiceRevenueService(BaseAnalyticsService, BaseAggregationService):
    
    def get_data(self, **filters) -> List[Dict]:
        start_date = filters.get('start_date')
        end_date = filters.get('end_date')
        
        services = []
        total_revenue = 0.0
        
        for service_type, service_label in ServiceTypeChoices.choices:
            data = self._calculate_service_metrics(service_type, start_date, end_date)
            
            if data['revenue'] > 0:
                services.append({
                    'name': service_label,
                    'type': service_type,
                    **data
                })
                total_revenue += data['revenue']
        
        self._add_percentages(services, total_revenue)
        
        return sorted(services, key=lambda x: x['revenue'], reverse=True)
    
    def _calculate_service_metrics(self, service_type: str, start_date=None, end_date=None) -> Dict:
        queryset = Income.objects.filter(service_type=service_type)
        queryset = self._apply_date_filters(queryset, start_date, end_date)
        
        aggregation = queryset.aggregate(
            total_revenue=Sum('amount'),
            count=Count('id'),
            avg_revenue=Avg('amount')
        )
        
        revenue = float(aggregation['total_revenue'] or 0)
        count = aggregation['count'] or 0
        avg_revenue = float(aggregation['avg_revenue'] or 0)
        
        return {
            'revenue': revenue,
            'count': count,
            'avg_revenue': avg_revenue,
        }
    
    def _add_percentages(self, services: List[Dict], total_revenue: float):
        for service in services:
            service['percentage'] = self._calculate_percentage(
                service['revenue'], 
                total_revenue
            )
