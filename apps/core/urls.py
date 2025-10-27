from django.urls import path
from .views.export import export_data

app_name = 'core'

urlpatterns = [
    path('export/', export_data, name='export_data'),
]
