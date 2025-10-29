from django.urls import path
from . import views

app_name = 'accounting'

urlpatterns = [
    path('', views.IncomeListView.as_view(), name='income_list'),
    path('income/add/', views.IncomeCreateView.as_view(), name='income_add'),
    path('income/<int:pk>/edit/', views.IncomeUpdateView.as_view(), name='income_edit'),
    path('income/<int:pk>/delete/', views.IncomeDeleteView.as_view(), name='income_delete'),
    path('summary/profit/', views.profit_summary_view, name='profit_summary'),
]
