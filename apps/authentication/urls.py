from django.urls import path
from .views import WestforceLoginView, WestforceLogoutView

app_name = 'authentication'

urlpatterns = [
    path('login/', WestforceLoginView.as_view(), name='login'),
    path('logout/', WestforceLogoutView.as_view(), name='logout'),
]
