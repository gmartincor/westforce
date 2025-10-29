from django.urls import path
from . import views, api_views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('api/expense-distribution/', api_views.expense_distribution_data, name='api_expense_distribution'),
    path('api/service-revenue/', api_views.service_revenue_data, name='api_service_revenue'),
]
