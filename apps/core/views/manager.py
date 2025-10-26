from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def manager_home(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    return render(request, 'manager/home_public.html', {
        'company_name': 'Westforce',
        'page_title': 'Manager Access'
    })
