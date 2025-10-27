from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('api/service-types/', views.get_filtered_service_types, name='api_service_types'),
    path('api/expenses/', views.get_filtered_expenses, name='api_expenses'),
]
