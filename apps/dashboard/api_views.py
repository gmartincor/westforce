from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from datetime import datetime
from .services import ExpenseDistributionService


@require_GET
@login_required
def expense_distribution_data(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    filters = {}
    
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
    
    service = ExpenseDistributionService()
    data = service.get_data(**filters)
    
    return JsonResponse(data, safe=False)
