from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class InitialSetupMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not self._is_setup_required(request):
            return self.get_response(request)
        
        if not self._is_setup_route(request) and not self._is_static_route(request):
            return redirect('authentication:setup')
        
        return self.get_response(request)
    
    def _is_setup_required(self, request):
        return not User.objects.filter(is_active=True).exists()
    
    def _is_setup_route(self, request):
        setup_urls = [
            reverse('authentication:setup'),
        ]
        return request.path in setup_urls
    
    def _is_static_route(self, request):
        static_prefixes = ['/static/', '/media/', '/admin/jsi18n/']
        return any(request.path.startswith(prefix) for prefix in static_prefixes)
