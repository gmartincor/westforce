from django.shortcuts import render
from django.contrib.auth import get_user_model

User = get_user_model()


def landing_page(request):
    company_name = 'Westforce'
    try:
        manager = User.objects.filter(is_active=True).first()
        if manager:
            company_name = getattr(manager, 'company_name', 'Westforce')
    except Exception:
        pass
    
    context = {
        'company_name': company_name,
        'company_tagline': 'Professional Australian Moving Company Management System',
        'features': [
            {
                'title': 'Client Management',
                'description': 'Comprehensive client database with service history',
                'icon': 'users'
            },
            {
                'title': 'Service Tracking',
                'description': 'Track all moving services and business lines',
                'icon': 'truck'
            },
            {
                'title': 'Invoice Generation',
                'description': 'Professional invoicing with PDF export',
                'icon': 'file-text'
            },
            {
                'title': 'Expense Management',
                'description': 'Track business expenses and profitability',
                'icon': 'dollar-sign'
            },
            {
                'title': 'Data Export',
                'description': 'Complete data portability in multiple formats',
                'icon': 'download'
            },
            {
                'title': 'Dashboard Analytics',
                'description': 'Real-time business metrics and reporting',
                'icon': 'bar-chart'
            }
        ]
    }
    return render(request, 'landing/index.html', context)
