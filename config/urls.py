from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.core.views.health import health_check
from apps.core.views.landing import landing_page

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('auth/', include('apps.authentication.urls')),
    path('core/', include('apps.core.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('accounting/', include('apps.accounting.urls')),
    path('expenses/', include('apps.expenses.urls')),
    path('invoicing/', include('apps.invoicing.urls')),
    path('', landing_page, name='landing_page'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
