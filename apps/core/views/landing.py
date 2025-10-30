from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


def landing_page(request):
    company_name = getattr(settings, 'COMPANY_NAME', 'Westforce')
    
    try:
        manager = User.objects.filter(is_active=True).first()
        if manager:
            company_name = getattr(manager, 'company_name', company_name)
    except Exception:
        pass
    
    context = {
        'company_name': company_name,
        'company_tagline': getattr(settings, 'COMPANY_TAGLINE', 'Professional Australian Moving Company Management System'),
        'meta_title': f'{company_name} - Professional Moving Services Perth',
        'meta_description': 'Expert moving and removalist services in Perth, Western Australia. Residential and commercial relocations with professional, reliable service. Get your free quote today.',
        'meta_keywords': 'moving company Perth, removalists Perth, furniture removals Perth, office relocation Perth, house movers Perth, professional movers WA, Perth moving services, relocation services Perth',
        'company_phone': '+61-8-1234-5678',
        'company_email': 'info@westforce.com',
        'features': [
            {
                'title': 'Client Management',
                'description': 'Comprehensive client database with complete service history and communication tracking',
                'icon': 'users'
            },
            {
                'title': 'Service Tracking',
                'description': 'Real-time tracking of all moving services across multiple business lines',
                'icon': 'truck'
            },
            {
                'title': 'Invoice Generation',
                'description': 'Professional automated invoicing with PDF export and payment tracking',
                'icon': 'file-text'
            },
            {
                'title': 'Expense Management',
                'description': 'Comprehensive expense tracking and profitability analysis',
                'icon': 'dollar-sign'
            },
            {
                'title': 'Data Export',
                'description': 'Complete data portability in multiple formats for business intelligence',
                'icon': 'download'
            },
            {
                'title': 'Dashboard Analytics',
                'description': 'Real-time business metrics, reporting, and performance insights',
                'icon': 'bar-chart'
            }
        ]
    }
    return render(request, 'landing/index.html', context)
