from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from apps.core.views.health import health_check
from apps.core.views.landing import landing_page
from apps.core.views.seo import robots_txt
from apps.core.sitemaps import StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('robots.txt', robots_txt, name='robots_txt'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
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
