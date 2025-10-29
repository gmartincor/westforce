from django.db.models import Sum, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
from typing import List, Dict
from apps.expenses.models import Expense, ExpenseCategory
from .base import BaseAnalyticsService


class ExpenseTrendService(BaseAnalyticsService):
    
    def __init__(self, months_back: int = 6):
        self.months_back = months_back
        self.today = timezone.now().date()
        self.start_date = self._calculate_start_date()
    
    def get_data(self, **filters) -> Dict:
        top_categories = self._get_top_categories()
        category_ids = [cat['id'] for cat in top_categories[:5]]
        
        monthly_data = self._get_monthly_trends(category_ids)
        
        return {
            'categories': top_categories[:5],
            'monthly_trends': monthly_data
        }
    
    def _calculate_start_date(self):
        months_ago = self.today.replace(day=1) - timedelta(days=30 * self.months_back)
        return months_ago
    
    def _get_top_categories(self) -> List[Dict]:
        categories = ExpenseCategory.objects.filter(
            is_active=True,
            expenses__date__gte=self.start_date
        ).annotate(
            total=Sum('expenses__amount')
        ).filter(
            total__isnull=False
        ).order_by('-total')[:5]
        
        return [
            {
                'id': cat.id,
                'name': cat.name,
                'total': float(cat.total or 0)
            }
            for cat in categories
        ]
    
    def _get_monthly_trends(self, category_ids: List[int]) -> List[Dict]:
        monthly_data = {}
        
        for cat_id in category_ids:
            expenses = Expense.objects.filter(
                category_id=cat_id,
                date__gte=self.start_date
            ).annotate(
                month=TruncMonth('date')
            ).values('month').annotate(
                total=Sum('amount')
            ).order_by('month')
            
            for item in expenses:
                month_key = item['month'].strftime('%Y-%m')
                if month_key not in monthly_data:
                    monthly_data[month_key] = {
                        'month': item['month'].strftime('%b %Y'),
                        'categories': {}
                    }
                monthly_data[month_key]['categories'][cat_id] = float(item['total'] or 0)
        
        return self._normalize_monthly_data(monthly_data, category_ids)
    
    def _normalize_monthly_data(self, monthly_data: Dict, category_ids: List[int]) -> List[Dict]:
        result = []
        current = self.start_date
        
        while current <= self.today:
            month_key = current.strftime('%Y-%m')
            
            if month_key in monthly_data:
                data = monthly_data[month_key]
            else:
                data = {
                    'month': current.strftime('%b %Y'),
                    'categories': {}
                }
            
            for cat_id in category_ids:
                if cat_id not in data['categories']:
                    data['categories'][cat_id] = 0
            
            result.append(data)
            current = self._next_month(current)
        
        return result[-self.months_back:]
    
    def _next_month(self, date):
        if date.month == 12:
            return date.replace(year=date.year + 1, month=1)
        return date.replace(month=date.month + 1)
