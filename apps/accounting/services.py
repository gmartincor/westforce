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
    
    def get_filtered_queryset(
        self,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        service_types: Optional[List[str]] = None
    ) -> QuerySet:
        queryset = self.get_all()
        
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        if service_types:
            queryset = queryset.filter(service_type__in=service_types)
        
        return queryset
    
    def get_profit_summary(
        self,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        service_types: Optional[List[str]] = None,
        expense_categories: Optional[List[str]] = None
    ) -> Dict:
        from apps.expenses.models import Expense
        
        income_queryset = self.get_filtered_queryset(date_from, date_to, service_types)
        revenue = income_queryset.aggregate(total=Sum('amount'))['total'] or 0
        
        expense_queryset = Expense.objects.all()
        
        if date_from:
            expense_queryset = expense_queryset.filter(date__gte=date_from)
        
        if date_to:
            expense_queryset = expense_queryset.filter(date__lte=date_to)
        
        if expense_categories:
            expense_queryset = expense_queryset.filter(category__category_type__in=expense_categories)
        
        expenses = expense_queryset.aggregate(total=Sum('amount'))['total'] or 0
        profit = revenue - expenses
        
        return {
            'revenue': revenue,
            'expenses': expenses,
            'profit': profit,
            'profit_margin': (profit / revenue * 100) if revenue > 0 else 0,
            'income_count': income_queryset.count(),
            'expense_count': expense_queryset.count(),
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
