from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


def landing_page(request):
    company_name = getattr(settings, 'COMPANY_NAME', 'Westforce Removals')
    
    try:
        manager = User.objects.filter(is_active=True).first()
        if manager:
            company_name = getattr(manager, 'company_name', company_name)
    except Exception:
        pass
    
    context = {
        'company_name': company_name,
        'company_phone': '+61 8 9234 5678',
        'company_email': 'info@westforceremovals.com.au',
    }
    return render(request, 'landing/home.html', context)


def privacy_policy(request):
    return render(request, 'landing/privacy-policy.html')


def terms_conditions(request):
    return render(request, 'landing/terms-conditions.html')
