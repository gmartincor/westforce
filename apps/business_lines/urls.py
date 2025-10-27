from django.urls import path
from . import views

app_name = 'business_lines'

urlpatterns = [
    path('', views.BusinessLineListView.as_view(), name='list'),
    path('create/', views.BusinessLineCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.BusinessLineUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.BusinessLineDeleteView.as_view(), name='delete'),
    path('<int:pk>/', views.BusinessLineDetailView.as_view(), name='detail'),
]
