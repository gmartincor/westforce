from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from django.db.models import QuerySet, Sum
from django.core.exceptions import ValidationError


class BaseService(ABC):
    
    def __init__(self, model_class=None):
        self.model_class = model_class
    
    def get_all(self, **filters) -> QuerySet:
        if not self.model_class:
            raise NotImplementedError("Model class not defined")
        return self.model_class.objects.filter(**filters)
    
    def get_by_id(self, id: int) -> Optional[Any]:
        if not self.model_class:
            raise NotImplementedError("Model class not defined")
        try:
            return self.model_class.objects.get(id=id)
        except self.model_class.DoesNotExist:
            return None
    
    def create(self, **data) -> Any:
        if not self.model_class:
            raise NotImplementedError("Model class not defined")
        instance = self.model_class(**data)
        instance.full_clean()
        instance.save()
        return instance
    
    def update(self, instance: Any, **data) -> Any:
        for field, value in data.items():
            setattr(instance, field, value)
        instance.full_clean()
        instance.save()
        return instance
    
    def delete(self, instance: Any) -> bool:
        try:
            instance.delete()
            return True
        except Exception:
            return False
    
    def validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return data


class FinancialService(BaseService):
    
    def get_by_accounting_period(self, year: int, month: Optional[int] = None) -> QuerySet:
        filters = {'accounting_year': year}
        if month:
            filters['accounting_month'] = month
        return self.get_all(**filters)
    
    def get_total_amount(self, queryset: Optional[QuerySet] = None) -> float:
        if queryset is None:
            queryset = self.get_all()
        return queryset.aggregate(total=Sum('amount'))['total'] or 0
    
    def get_monthly_summary(self, year: int) -> Dict[int, float]:
        queryset = self.get_all(accounting_year=year)
        return {
            month_data['accounting_month']: month_data['total']
            for month_data in queryset.values('accounting_month')
            .annotate(total=Sum('amount'))
            .order_by('accounting_month')
        }


class ValidationMixin:
    
    def validate_positive_amount(self, amount: float) -> float:
        if amount <= 0:
            raise ValidationError("Amount must be greater than zero")
        return amount
    
    def validate_date_range(self, start_date, end_date):
        if start_date and end_date and start_date > end_date:
            raise ValidationError("Start date cannot be after end date")
        return start_date, end_date
