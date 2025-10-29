from abc import ABC, abstractmethod
from typing import Any, Dict, List
from django.db.models import QuerySet


class BaseAnalyticsService(ABC):
    
    @abstractmethod
    def get_data(self, **filters) -> Any:
        pass


class BaseAggregationService(ABC):
    
    def _apply_date_filters(self, queryset: QuerySet, start_date=None, end_date=None, date_field='date') -> QuerySet:
        if start_date:
            queryset = queryset.filter(**{f'{date_field}__gte': start_date})
        if end_date:
            queryset = queryset.filter(**{f'{date_field}__lte': end_date})
        return queryset
    
    def _calculate_percentage(self, part: float, total: float) -> float:
        return (part / total * 100) if total > 0 else 0
