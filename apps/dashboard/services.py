from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta

from apps.accounting.models import Income
from apps.expenses.models import Expense, ExpenseCategory
from apps.business_lines.models import BusinessLine


class FinancialSummaryService:
    
    @staticmethod
    def get_summary():
        today = timezone.now().date()
        month_start = today.replace(day=1)
        
        total_income = Income.objects.aggregate(total=Sum('amount'))['total'] or 0
        monthly_income = Income.objects.filter(
            date__gte=month_start
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        total_expenses = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
        monthly_expenses = Expense.objects.filter(
            date__gte=month_start
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        total_profit = total_income - total_expenses
        monthly_profit = monthly_income - monthly_expenses
        
        profit_margin = (total_profit / total_income * 100) if total_income > 0 else 0
        monthly_profit_margin = (monthly_profit / monthly_income * 100) if monthly_income > 0 else 0
        
        return {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'total_profit': total_profit,
            'monthly_income': monthly_income,
            'monthly_expenses': monthly_expenses,
            'monthly_profit': monthly_profit,
            'profit_margin': profit_margin,
            'monthly_profit_margin': monthly_profit_margin,
        }


class TemporalDataService:
    
    @staticmethod
    def get_monthly_data(months_back=12):
        today = timezone.now().date()
        start_date = today.replace(day=1) - timedelta(days=365)
        
        monthly_income = Income.objects.filter(
            date__gte=start_date
        ).annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            total=Sum('amount')
        ).order_by('month')
        
        monthly_expenses = Expense.objects.filter(
            date__gte=start_date
        ).annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            total=Sum('amount')
        ).order_by('month')
        
        income_dict = {item['month'].strftime('%Y-%m'): float(item['total'] or 0) for item in monthly_income}
        expenses_dict = {item['month'].strftime('%Y-%m'): float(item['total'] or 0) for item in monthly_expenses}
        
        months = []
        current_date = start_date
        while current_date <= today:
            month_key = current_date.strftime('%Y-%m')
            income = income_dict.get(month_key, 0)
            expenses = expenses_dict.get(month_key, 0)
            
            months.append({
                'month': current_date.strftime('%b %Y'),
                'income': income,
                'expenses': expenses,
                'profit': income - expenses
            })
            
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        return months[-months_back:]


class BusinessLineAnalyticsService:
    
    @staticmethod
    def get_performance_data(start_date=None, end_date=None, level=None):
        queryset = BusinessLine.objects.filter(is_active=True)
        
        if level:
            queryset = queryset.filter(level=level)
        
        business_lines = []
        
        for line in queryset:
            income_filter = Q(business_line=line)
            
            if start_date:
                income_filter &= Q(date__gte=start_date)
            if end_date:
                income_filter &= Q(date__lte=end_date)
            
            incomes = Income.objects.filter(income_filter)
            total_revenue = incomes.aggregate(total=Sum('amount'))['total'] or 0
            service_count = incomes.count()
            
            business_lines.append({
                'name': line.name,
                'total_revenue': total_revenue,
                'service_count': service_count,
            })
        
        business_lines.sort(key=lambda x: x['total_revenue'], reverse=True)
        total_revenue = sum(line['total_revenue'] for line in business_lines)
        
        for line in business_lines:
            line['percentage'] = (line['total_revenue'] / total_revenue * 100) if total_revenue > 0 else 0
        
        return business_lines


class ExpenseCategoryAnalyticsService:
    
    @staticmethod
    def get_category_breakdown(start_date=None, end_date=None):
        expense_filter = Q()
        if start_date:
            expense_filter &= Q(expenses__date__gte=start_date)
        if end_date:
            expense_filter &= Q(expenses__date__lte=end_date)
        
        categories_data = ExpenseCategory.objects.filter(
            is_active=True
        ).annotate(
            total=Sum('expenses__amount', filter=expense_filter),
            count=Count('expenses', filter=expense_filter)
        ).filter(total__isnull=False).order_by('-total')
        
        categories = []
        total_expenses = 0
        
        for category in categories_data:
            category_total = getattr(category, 'total', 0) or 0
            category_count = getattr(category, 'count', 0) or 0
            
            categories.append({
                'category': category,
                'name': category.name,
                'total': category_total,
                'count': category_count
            })
            total_expenses += category_total
        
        for category_data in categories:
            category_data['percentage'] = (
                category_data['total'] / total_expenses * 100
            ) if total_expenses > 0 and category_data['total'] else 0
        
        return categories


class DashboardDataService:
    
    def __init__(self):
        self.financial_service = FinancialSummaryService()
        self.temporal_service = TemporalDataService()
        self.business_line_service = BusinessLineAnalyticsService()
        self.expense_service = ExpenseCategoryAnalyticsService()
    
    def get_financial_summary(self):
        return self.financial_service.get_summary()
    
    def get_temporal_data(self):
        return self.temporal_service.get_monthly_data()
    
    def get_business_lines_data(self, start_date=None, end_date=None, level=None):
        return self.business_line_service.get_performance_data(start_date, end_date, level)
    
    def get_expense_categories_data(self, start_date=None, end_date=None):
        return self.expense_service.get_category_breakdown(start_date, end_date)
