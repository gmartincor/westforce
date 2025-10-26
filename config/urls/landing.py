from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from apps.core.views.landing import landing_page
from apps.core.views.health import health_check


app_name = 'landing'

urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('', landing_page, name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
