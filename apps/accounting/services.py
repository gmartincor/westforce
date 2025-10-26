from ..core.services.base import FinancialService, ValidationMixin
from .models import Income, ServiceTypeChoices
from ..business_lines.models import BusinessLine
from typing import Dict, List, Optional
from django.db.models import QuerySet, Sum, Q, Count
from datetime import date


class IncomeService(FinancialService, ValidationMixin):
    
    def __init__(self):
        super().__init__(Income)
    
    def get_by_business_line(self, business_line_id: int) -> QuerySet:
        return self.get_all(business_line_id=business_line_id)
    
    def get_by_service_type(self, service_type: str) -> QuerySet:
        return self.get_all(service_type=service_type)
    
    def get_by_date_range(self, start_date: date, end_date: date) -> QuerySet:
        self.validate_date_range(start_date, end_date)
        return self.get_all(date__range=[start_date, end_date])
    
    def get_revenue_by_location(self, year: int, month: Optional[int] = None) -> Dict[str, float]:
        filters = {'accounting_year': year}
        if month:
            filters['accounting_month'] = month
        
        queryset = self.get_all(**filters).select_related('business_line')
        
        location_revenue = {}
        for income in queryset:
            location = income.business_line.location or 'Unknown'
            location_revenue[location] = location_revenue.get(location, 0) + float(income.amount)
        
        return location_revenue
    
    def get_service_performance(self, year: int) -> Dict[str, Dict]:
        queryset = self.get_all(accounting_year=year)
        
        performance = {}
        for choice in ServiceTypeChoices.choices:
            service_type = choice[0]
            service_data = queryset.filter(service_type=service_type)
            
            performance[service_type] = {
                'label': choice[1],
                'total_revenue': service_data.aggregate(total=Sum('amount'))['total'] or 0,
                'count': service_data.count(),
                'average': (service_data.aggregate(total=Sum('amount'))['total'] or 0) / max(service_data.count(), 1)
            }
        
        return performance
    
    def create_income(self, **data) -> Income:
        self.validate_positive_amount(data.get('amount', 0))
        return self.create(**data)
    
    def get_top_clients(self, limit: int = 10, year: Optional[int] = None) -> List[Dict]:
        queryset = self.get_all()
        if year:
            queryset = queryset.filter(accounting_year=year)
        
        client_revenue = queryset.exclude(
            Q(client_name='') | Q(client_name__isnull=True)
        ).values('client_name').annotate(
            total_revenue=Sum('amount'),
            service_count=Count('id')
        ).order_by('-total_revenue')[:limit]
        
        return list(client_revenue)
