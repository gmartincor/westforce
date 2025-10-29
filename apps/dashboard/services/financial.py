from django.db.models import Sum
from django.utils import timezone
from apps.accounting.models import Income
from apps.expenses.models import Expense
from .base import BaseAnalyticsService


class FinancialMetricsService(BaseAnalyticsService):
    
    def __init__(self):
        self.today = timezone.now().date()
        self.month_start = self.today.replace(day=1)
    
    def get_data(self, **filters):
        return {
            **self._get_income_metrics(),
            **self._get_expense_metrics(),
            **self._get_profit_metrics(),
        }
    
    def _get_income_metrics(self) -> dict:
        total = self._aggregate_income()
        monthly = self._aggregate_income(start_date=self.month_start)
        
        return {
            'total_income': total,
            'monthly_income': monthly,
        }
    
    def _get_expense_metrics(self) -> dict:
        total = self._aggregate_expenses()
        monthly = self._aggregate_expenses(start_date=self.month_start)
        
        return {
            'total_expenses': total,
            'monthly_expenses': monthly,
        }
    
    def _get_profit_metrics(self) -> dict:
        total_income = self._aggregate_income()
        total_expenses = self._aggregate_expenses()
        monthly_income = self._aggregate_income(start_date=self.month_start)
        monthly_expenses = self._aggregate_expenses(start_date=self.month_start)
        
        total_profit = total_income - total_expenses
        monthly_profit = monthly_income - monthly_expenses
        
        profit_margin = (total_profit / total_income * 100) if total_income > 0 else 0
        monthly_profit_margin = (monthly_profit / monthly_income * 100) if monthly_income > 0 else 0
        
        return {
            'total_profit': total_profit,
            'monthly_profit': monthly_profit,
            'profit_margin': profit_margin,
            'monthly_profit_margin': monthly_profit_margin,
        }
    
    def _aggregate_income(self, start_date=None, end_date=None) -> float:
        queryset = Income.objects.all()
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        return float(queryset.aggregate(total=Sum('amount'))['total'] or 0)
    
    def _aggregate_expenses(self, start_date=None, end_date=None) -> float:
        queryset = Expense.objects.all()
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        return float(queryset.aggregate(total=Sum('amount'))['total'] or 0)
