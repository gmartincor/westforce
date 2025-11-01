from django.shortcuts import render


def privacy_policy(request):
    return render(request, 'landing/privacy-policy.html')


def terms_conditions(request):
    return render(request, 'landing/terms-conditions.html')
