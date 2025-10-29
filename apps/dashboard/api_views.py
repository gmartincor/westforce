from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from datetime import datetime
from .services import ExpenseDistributionService, ServiceRevenueService


def parse_date_filters(request):
    filters = {}
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        try:
            filters['start_date'] = datetime.fromisoformat(start_date).date()
        except (ValueError, TypeError):
            pass
    
    if end_date:
        try:
            filters['end_date'] = datetime.fromisoformat(end_date).date()
        except (ValueError, TypeError):
            pass
    
    return filters


@require_GET
@login_required
def expense_distribution_data(request):
    service = ExpenseDistributionService()
    data = service.get_data(**parse_date_filters(request))
    return JsonResponse(data, safe=False)


@require_GET
@login_required
def service_revenue_data(request):
    service = ServiceRevenueService()
    data = service.get_data(**parse_date_filters(request))
    return JsonResponse(data, safe=False)
