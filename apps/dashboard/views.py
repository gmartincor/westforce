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
        }
    
    def get_dashboard_context(self):
        return {
            **self.service.get_financial_summary(),
            'temporal_data': self.service.get_temporal_data(),
            'service_types': self.service.get_service_types_data(),
            'expense_categories': self.service.get_expense_categories_data(),
            'payment_methods': self.service.get_payment_methods_data(),
            'top_clients': self.service.get_top_clients(),
        }


@login_required
def dashboard_home(request):
    handler = DashboardDataHandler()
    context = handler.get_dashboard_context()
    return render(request, 'dashboard/home.html', context)


@login_required
def get_filtered_service_types(request):
    handler = DashboardDataHandler()
    filters = handler.get_filter_params(request)
    
    service_types = handler.service.get_service_types_data(**filters)
    
    return JsonResponse({
        'service_types_data': [
            {
                'name': st['name'],
                'revenue': float(st['total_revenue']),
                'percentage': float(st['percentage'])
            }
            for st in service_types
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
