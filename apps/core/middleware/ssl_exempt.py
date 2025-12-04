class SSLExemptMiddleware:
    EXEMPT_URLS = ['/health/', '/health']
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.path in self.EXEMPT_URLS:
            request.is_secure = lambda: True
        return self.get_response(request)
