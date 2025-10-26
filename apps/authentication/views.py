from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views import View
from .forms.setup_form import SingleUserSetupForm

User = get_user_model()


@method_decorator([
    sensitive_post_parameters(),
    csrf_protect,
    never_cache,
], name='dispatch')
class WestforceLoginView(LoginView):
    template_name = 'authentication/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('dashboard:home')
    
    def dispatch(self, request, *args, **kwargs):
        if not User.objects.filter(is_active=True).exists():
            return redirect('authentication:setup')
        return super().dispatch(request, *args, **kwargs)
    
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
    next_page = reverse_lazy('authentication:login')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.success(request, 'You have been successfully logged out.')
        return super().dispatch(request, *args, **kwargs)


class SetupView(View):
    template_name = 'authentication/setup.html'
    
    def get(self, request):
        if User.objects.filter(is_active=True).exists():
            messages.info(request, 'System has already been configured.')
            return redirect('authentication:login')
        
        form = SingleUserSetupForm()
        return render(request, self.template_name, {
            'form': form,
            'app_name': 'Westforce',
            'page_title': 'Initial Setup'
        })
    
    def post(self, request):
        if User.objects.filter(is_active=True).exists():
            messages.error(request, 'System has already been configured.')
            return redirect('authentication:login')
        
        form = SingleUserSetupForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f'System configured successfully. User {user.username} created.'
            )
            return redirect('authentication:login')
        
        return render(request, self.template_name, {
            'form': form,
            'app_name': 'Westforce',
            'page_title': 'Initial Setup'
        })
