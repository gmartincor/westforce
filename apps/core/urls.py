from django.urls import path
from .views.export import export_data
from .views import quote_request, privacy_policy, terms_conditions

app_name = 'core'

urlpatterns = [
    path('export/', export_data, name='export_data'),
    path('quote/', quote_request, name='quote_request'),
    path('privacy-policy/', privacy_policy, name='privacy_policy'),
    path('terms-conditions/', terms_conditions, name='terms_conditions'),
]
