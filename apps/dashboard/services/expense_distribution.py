from django.db.models import Sum
from typing import List, Dict
from apps.expenses.models import Expense
from .base import BaseAnalyticsService, BaseAggregationService


class ExpenseDistributionService(BaseAnalyticsService, BaseAggregationService):
    
    def get_data(self, **filters) -> List[Dict]:
        start_date = filters.get('start_date')
        end_date = filters.get('end_date')
        
        categories = self._get_category_totals(start_date, end_date)
        total_expenses = sum(cat['total'] for cat in categories)
        
        for category in categories:
            category['percentage'] = self._calculate_percentage(
                category['total'], 
                total_expenses
            )
        
        return categories
    
    def _get_category_totals(self, start_date=None, end_date=None) -> List[Dict]:
        queryset = Expense.objects.select_related('category').filter(
            category__is_active=True
        )
        
        queryset = self._apply_date_filters(queryset, start_date, end_date)
        
        category_totals = queryset.values(
            'category__id',
            'category__name'
        ).annotate(
            total=Sum('amount'),
        ).order_by('-total')
        
        return [
            {
                'name': item['category__name'],
                'total': float(item['total'] or 0),
            }
            for item in category_totals if item['total']
        ]
