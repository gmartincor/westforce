from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

User = get_user_model()


class SingleUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/') or request.path.startswith('/auth/'):
            return self.get_response(request)

        if not User.objects.filter(is_active=True).exists():
            if not request.path.startswith('/auth/setup/'):
                messages.warning(
                    request,
                    'El sistema requiere configuración inicial. Configure el usuario administrador.'
                )
                return redirect(reverse('authentication:setup'))

        response = self.get_response(request)
        return response
