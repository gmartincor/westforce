from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
from typing import List, Dict
from apps.accounting.models import Income
from apps.expenses.models import Expense
from .base import BaseAnalyticsService


class CashFlowService(BaseAnalyticsService):
    
    def __init__(self, months_back: int = 12):
        self.months_back = months_back
        self.today = timezone.now().date()
        self.start_date = self._calculate_start_date()
    
    def get_data(self, **filters) -> List[Dict]:
        income_data = self._get_monthly_income()
        expense_data = self._get_monthly_expenses()
        
        income_dict = {item['month'].strftime('%Y-%m'): float(item['total'] or 0) for item in income_data}
        expense_dict = {item['month'].strftime('%Y-%m'): float(item['total'] or 0) for item in expense_data}
        
        return self._build_monthly_series(income_dict, expense_dict)
    
    def _calculate_start_date(self):
        return self.today.replace(day=1) - timedelta(days=365)
    
    def _get_monthly_income(self):
        return Income.objects.filter(
            date__gte=self.start_date
        ).annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            total=Sum('amount')
        ).order_by('month')
    
    def _get_monthly_expenses(self):
        return Expense.objects.filter(
            date__gte=self.start_date
        ).annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            total=Sum('amount')
        ).order_by('month')
    
    def _build_monthly_series(self, income_dict: Dict, expense_dict: Dict) -> List[Dict]:
        months = []
        current = self.start_date
        
        while current <= self.today:
            month_key = current.strftime('%Y-%m')
            income = income_dict.get(month_key, 0)
            expenses = expense_dict.get(month_key, 0)
            
            months.append({
                'month': current.strftime('%b %Y'),
                'income': income,
                'expenses': expenses,
                'cash_flow': income - expenses
            })
            
            current = self._next_month(current)
        
        return months[-self.months_back:]
    
    def _next_month(self, date):
        if date.month == 12:
            return date.replace(year=date.year + 1, month=1)
        return date.replace(month=date.month + 1)
