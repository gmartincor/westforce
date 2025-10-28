from apps.core.services.base import FinancialService, ValidationMixin
from .models import Income, ServiceTypeChoices
from typing import Dict, List, Optional
from django.db.models import QuerySet, Sum, Count, Q
from django.utils import timezone
from datetime import date


class IncomeService(FinancialService, ValidationMixin):
    
    def __init__(self):
        super().__init__(Income)
    
    def get_by_service_type(self, service_type: str) -> QuerySet:
        return self.get_all(service_type=service_type)
    
    def get_by_date_range(self, start_date: date, end_date: date) -> QuerySet:
        self.validate_date_range(start_date, end_date)
        return self.get_all(date__range=[start_date, end_date])
    
    def get_revenue_summary(self, year: Optional[int] = None) -> Dict:
        if year is None:
            year = timezone.now().year
        
        revenue_data = self.get_all(accounting_year=year).aggregate(
            total=Sum('amount'),
            count=Count('id')
        )
        
        total = revenue_data['total'] or 0
        count = revenue_data['count'] or 0
        
        return {
            'year': year,
            'total_revenue': total,
            'total_services': count,
            'average_revenue': total / max(count, 1),
        }
    
    def get_profit_summary(self, year: Optional[int] = None) -> Dict:
        from apps.expenses.models import Expense
        
        if year is None:
            year = timezone.now().year
        
        revenue = self.get_all(accounting_year=year).aggregate(total=Sum('amount'))['total'] or 0
        expenses = Expense.objects.filter(date__year=year).aggregate(total=Sum('amount'))['total'] or 0
        profit = revenue - expenses
        
        return {
            'year': year,
            'revenue': revenue,
            'expenses': expenses,
            'profit': profit,
            'profit_margin': (profit / revenue * 100) if revenue > 0 else 0,
        }
    
    def get_service_performance(self, year: int) -> Dict[str, Dict]:
        queryset = self.get_all(accounting_year=year)
        
        performance = {}
        for choice in ServiceTypeChoices.choices:
            service_type = choice[0]
            service_data = queryset.filter(service_type=service_type)
            total = service_data.aggregate(total=Sum('amount'))['total'] or 0
            count = service_data.count()
            
            performance[service_type] = {
                'label': choice[1],
                'total_revenue': total,
                'count': count,
                'average': total / max(count, 1)
            }
        
        return performance
    
    def create_income(self, **data) -> Income:
        self.validate_positive_amount(data.get('amount', 0))
        return self.create(**data)
    
    def get_top_clients(self, limit: int = 10, year: Optional[int] = None) -> List[Dict]:
        queryset = self.get_all()
        if year:
            queryset = queryset.filter(accounting_year=year)
        
        return list(
            queryset.exclude(Q(client_name='') | Q(client_name__isnull=True))
            .values('client_name')
            .annotate(total_revenue=Sum('amount'), service_count=Count('id'))
            .order_by('-total_revenue')[:limit]
        )
