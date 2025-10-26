from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from .services import DashboardDataService


class DashboardDataHandler:
    
    def __init__(self):
        self.service = DashboardDataService()
    
    def get_filter_params(self, request):
        return {
            'start_date': parse_date(request.GET.get('start_date')) if request.GET.get('start_date') else None,
            'end_date': parse_date(request.GET.get('end_date')) if request.GET.get('end_date') else None,
            'level': int(request.GET.get('level')) if request.GET.get('level') else None
        }
    
    def get_dashboard_context(self):
        return {
            **self.service.get_financial_summary(),
            'temporal_data': self.service.get_temporal_data(),
            'business_lines': self.service.get_business_lines_data(),
            'expense_categories': self.service.get_expense_categories_data(),
        }


@login_required
def dashboard_home(request):
    handler = DashboardDataHandler()
    context = handler.get_dashboard_context()
    return render(request, 'dashboard/home.html', context)


@login_required
def get_filtered_business_lines(request):
    handler = DashboardDataHandler()
    filters = handler.get_filter_params(request)
    
    business_lines = handler.service.get_business_lines_data(**filters)
    
    return JsonResponse({
        'business_lines_data': [
            {
                'name': line['name'],
                'revenue': float(line['total_revenue']),
                'percentage': float(line['percentage'])
            }
            for line in business_lines
        ]
    })


@login_required
def get_filtered_expenses(request):
    handler = DashboardDataHandler()
    filters = handler.get_filter_params(request)
    
    expense_categories = handler.service.get_expense_categories_data(
        filters['start_date'], 
        filters['end_date']
    )
    
    return JsonResponse({
        'expenses_data': [
            {
                'category': category['name'],
                'total': float(category['total']),
                'percentage': float(category['percentage'])
            }
            for category in expense_categories
        ]
    })
