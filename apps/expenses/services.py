from ..core.services.base import FinancialService, ValidationMixin
from .models import Expense, ExpenseCategory
from typing import Dict, List, Optional
from django.db.models import QuerySet, Sum, Count
from datetime import date


class ExpenseService(FinancialService, ValidationMixin):
    
    def __init__(self):
        super().__init__(Expense)
    
    def get_by_category(self, category_id: int) -> QuerySet:
        return self.get_all(category_id=category_id)
    
    def get_by_service_category(self, service_category: str) -> QuerySet:
        return self.get_all(service_category=service_category)
    
    def get_by_date_range(self, start_date: date, end_date: date) -> QuerySet:
        self.validate_date_range(start_date, end_date)
        return self.get_all(date__range=[start_date, end_date])
    
    def get_expenses_by_category_type(self, year: int, month: Optional[int] = None) -> Dict[str, float]:
        filters = {'accounting_year': year}
        if month:
            filters['accounting_month'] = month
        
        queryset = self.get_all(**filters).select_related('category')
        
        category_expenses = {}
        for expense in queryset:
            category_type = expense.category.get_category_type_display()
            category_expenses[category_type] = category_expenses.get(category_type, 0) + float(expense.amount)
        
        return category_expenses
    
    def create_expense(self, **data) -> Expense:
        self.validate_positive_amount(data.get('amount', 0))
        return self.create(**data)
    
    def get_top_expense_categories(self, limit: int = 10, year: Optional[int] = None) -> List[Dict]:
        queryset = self.get_all()
        if year:
            queryset = queryset.filter(accounting_year=year)
        
        category_expenses = queryset.select_related('category').values(
            'category__name', 'category__category_type'
        ).annotate(
            total_amount=Sum('amount'),
            expense_count=Count('id')
        ).order_by('-total_amount')[:limit]
        
        return list(category_expenses)


class ExpenseCategoryService(ValidationMixin):
    
    def __init__(self):
        self.model_class = ExpenseCategory
    
    def get_active_categories(self) -> QuerySet:
        return ExpenseCategory.objects.filter(is_active=True)
    
    def get_by_category_type(self, category_type: str) -> QuerySet:
        return ExpenseCategory.objects.filter(category_type=category_type, is_active=True)
    
    def create_category(self, **data) -> ExpenseCategory:
        return ExpenseCategory.objects.create(**data)
