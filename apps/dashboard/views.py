from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .services import DashboardOrchestrator


@login_required
def dashboard_home(request):
    orchestrator = DashboardOrchestrator()
    context = orchestrator.get_dashboard_data()
    return render(request, 'dashboard/home.html', context)
