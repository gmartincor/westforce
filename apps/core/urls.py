from django.urls import path
from .views.export import export_data
from .views import quote_request

app_name = 'core'

urlpatterns = [
    path('export/', export_data, name='export_data'),
    path('quote/', quote_request, name='quote_request'),
]
