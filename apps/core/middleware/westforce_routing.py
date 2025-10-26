from django.http import HttpResponsePermanentRedirect
from django.urls import set_urlconf
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.conf import settings


class WestforceRoutingMiddleware(MiddlewareMixin):
    
    BYPASS_PATHS = [
        '/static/',
        '/media/',
        '/admin/jsi18n/',
        '/health/',
        '/favicon.ico'
    ]
    MANAGER_ONLY_PATHS = [
        '/dashboard/',
        '/accounting/',
        '/expenses/',
        '/invoicing/',
        '/admin/'
    ]
    
    def process_request(self, request):
        host = request.get_host().lower()
        
        if ':' in host:
            host = host.split(':')[0]
        
        dev_mode = getattr(settings, 'DEV_FORCE_LANDING', False)
        is_manager_domain = self._is_manager_domain(host, dev_mode)
        
        if host.startswith('www.') and not is_manager_domain:
            redirect_url = f"{request.scheme}://{host[4:]}{request.get_full_path()}"
            return HttpResponsePermanentRedirect(redirect_url)
        
        if is_manager_domain:
            set_urlconf('config.urls.manager')
            request.urlconf = 'config.urls.manager'
        else:
            set_urlconf('config.urls.landing')
            request.urlconf = 'config.urls.landing'
        
        if self._should_bypass_checks(request.path):
            return None
        
        if is_manager_domain:
            return self._handle_manager_domain(request)
        
        return self._handle_main_domain(request, host)
    
    def _is_manager_domain(self, host, dev_mode=False):
        if dev_mode:
            return False
        
        return (
            host.startswith('manager.') or 
            host in ['localhost', '127.0.0.1'] or
            'manager' in host
        )
    
    def _should_bypass_checks(self, path):
        return any(path.startswith(prefix) for prefix in self.BYPASS_PATHS)
    
    def _handle_manager_domain(self, request):
        if self._is_manager_only_path(request.path) and not request.user.is_authenticated:
            return redirect('authentication:login')
        
        return None
    
    def _handle_main_domain(self, request, host):
        if self._is_manager_only_path(request.path):
            manager_url = f"{request.scheme}://manager.{host}{request.get_full_path()}"
            return redirect(manager_url)
        
        return None
    
    def _is_manager_only_path(self, path):
        return any(path.startswith(prefix) for prefix in self.MANAGER_ONLY_PATHS)
