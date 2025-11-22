from django.shortcuts import render


def landing_page(request):
    return render(request, 'landing/home.html')


def privacy_policy(request):
    return render(request, 'landing/privacy-policy.html')


def terms_conditions(request):
    return render(request, 'landing/terms-conditions.html')
