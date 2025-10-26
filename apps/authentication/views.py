from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters


@method_decorator([
    sensitive_post_parameters(),
    csrf_protect,
    never_cache,
], name='dispatch')
class WestforceLoginView(LoginView):
    template_name = 'authentication/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('dashboard:home')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'app_name': 'Westforce',
            'page_title': 'Sign In',
            'show_register': False,
        })
        return context
    
    def form_valid(self, form):
        messages.success(
            self.request, 
            f'Welcome back, {form.get_user().get_full_name() or form.get_user().username}!'
        )
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(
            self.request, 
            'Invalid credentials. Please check your username and password.'
        )
        return super().form_invalid(form)


class WestforceLogoutView(LogoutView):
    next_page = reverse_lazy('landing_page')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.success(request, 'You have been successfully logged out.')
        return super().dispatch(request, *args, **kwargs)
