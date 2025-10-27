from django.urls import path
from . import views

app_name = 'accounting'

urlpatterns = [
    path('', views.IncomeListView.as_view(), name='income_list'),
    path('income/add/', views.IncomeCreateView.as_view(), name='income_add'),
    path('income/<int:pk>/edit/', views.IncomeUpdateView.as_view(), name='income_edit'),
    path('income/<int:pk>/delete/', views.IncomeDeleteView.as_view(), name='income_delete'),
    
    path('business-lines/', views.business_lines_view, name='business_lines'),
    
    path('summary/revenue/<str:category>/', views.revenue_summary_view, name='revenue_summary'),
    path('summary/profit/<str:category>/', views.profit_summary_view, name='profit_summary'),
]
