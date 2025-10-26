from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin


class AuthRedirectMiddleware(MiddlewareMixin):
    
    BYPASS_PATHS = [
        '/static/',
        '/media/',
        '/admin/jsi18n/',
        '/health/',
        '/favicon.ico',
        '/auth/',
    ]
    
    PROTECTED_PATHS = [
        '/dashboard/',
        '/accounting/',
        '/expenses/',
        '/invoicing/',
        '/admin/',
    ]
    
    def process_request(self, request):
        if self._should_bypass_checks(request.path):
            return None
        
        if self._is_protected_path(request.path) and not request.user.is_authenticated:
            return redirect('authentication:login')
        
        return None
    
    def _should_bypass_checks(self, path):
        return any(path.startswith(prefix) for prefix in self.BYPASS_PATHS)
    
    def _is_protected_path(self, path):
        return any(path.startswith(prefix) for prefix in self.PROTECTED_PATHS)
