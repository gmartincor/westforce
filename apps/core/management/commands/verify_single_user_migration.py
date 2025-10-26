from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


class Command(BaseCommand):
    help = 'Verifica que la migración a single-user esté completa'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                '🔍 Verificando migración a sistema single-user\n'
                '=' * 50
            )
        )

        errors = []
        warnings = []

        self._check_user_system(errors, warnings)
        self._check_configuration(errors, warnings)
        self._check_middleware(errors, warnings)
        self._check_urls(errors, warnings)

        self._show_summary(errors, warnings)

    def _check_user_system(self, errors, warnings):
        self.stdout.write('\n👤 Sistema de usuarios:')
        
        user_count = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        
        if user_count == 0:
            warnings.append('No hay usuarios en el sistema')
            self.stdout.write('   ⚠️  Sin usuarios - redirección automática al setup')
        elif user_count == 1:
            user = User.objects.first()
            self.stdout.write(f'   ✅ Usuario único: {user.username} ({user.email})')
            if user.is_superuser:
                self.stdout.write('   ✅ Usuario con permisos de administrador')
            else:
                warnings.append('El usuario único no tiene permisos de administrador')
        else:
            warnings.append(f'Hay {user_count} usuarios en el sistema')
            self.stdout.write(f'   ⚠️  {user_count} usuarios (recomendado: 1 usuario único)')

    def _check_configuration(self, errors, warnings):
        self.stdout.write('\n⚙️  Configuración:')
        
        if hasattr(settings, 'DOMAIN'):
            self.stdout.write(f'   ✅ DOMAIN configurado: {settings.DOMAIN}')
        else:
            warnings.append('Variable DOMAIN no configurada')
            
        if 'manager.westforce.com.au' in settings.ALLOWED_HOSTS:
            self.stdout.write('   ✅ ALLOWED_HOSTS incluye manager.westforce.com.au')
        else:
            warnings.append('ALLOWED_HOSTS no incluye manager.westforce.com.au')
            
        middleware = settings.MIDDLEWARE
        if 'apps.core.middleware.SingleUserSetupMiddleware' in middleware:
            self.stdout.write('   ✅ Middleware de setup automático configurado')
        else:
            warnings.append('Middleware de setup automático no configurado')

    def _check_middleware(self, errors, warnings):
        self.stdout.write('\n🔧 Middleware:')
        
        middleware = settings.MIDDLEWARE
        if 'apps.core.middleware.DomainRoutingMiddleware' in middleware:
            errors.append('Middleware multitenant DomainRoutingMiddleware aún presente')
        else:
            self.stdout.write('   ✅ Middleware multitenant eliminado')

    def _check_urls(self, errors, warnings):
        self.stdout.write('\n🔗 URLs:')
        
        try:
            from django.urls import reverse
            
            try:
                landing_url = reverse('landing_page')
                self.stdout.write('   ✅ Landing page configurada')
            except:
                warnings.append('Landing page no configurada')
                
            try:
                setup_url = reverse('authentication:setup')
                self.stdout.write('   ✅ URL de setup configurada')
            except:
                errors.append('URL de setup no configurada')
                
        except Exception as e:
            warnings.append(f'Error verificando URLs: {e}')

    def _show_summary(self, errors, warnings):
        self.stdout.write('\n' + '=' * 50)
        
        if errors:
            self.stdout.write(self.style.ERROR(f'❌ {len(errors)} ERROR(ES) ENCONTRADO(S):'))
            for error in errors:
                self.stdout.write(self.style.ERROR(f'   • {error}'))
        
        if warnings:
            self.stdout.write(self.style.WARNING(f'⚠️  {len(warnings)} ADVERTENCIA(S):'))
            for warning in warnings:
                self.stdout.write(self.style.WARNING(f'   • {warning}'))
        
        if not errors and not warnings:
            self.stdout.write(
                self.style.SUCCESS(
                    '🎉 ¡Migración a single-user completada exitosamente!\n'
                    '   El sistema está listo para westforce.com.au'
                )
            )
            self._show_next_steps()
        elif not errors:
            self.stdout.write(
                self.style.SUCCESS(
                    '✅ Migración básica completada con algunas advertencias'
                )
            )
            self._show_next_steps()
        else:
            self.stdout.write(
                self.style.ERROR(
                    '❌ La migración necesita correcciones antes de continuar'
                )
            )

    def _show_next_steps(self):
        self.stdout.write('\n📋 PRÓXIMOS PASOS:')
        self.stdout.write('1. Configurar DNS para westforce.com.au y manager.westforce.com.au')
        self.stdout.write('2. Configurar variables de entorno en Render')
        self.stdout.write('3. Desplegar en producción')
        self.stdout.write('4. Verificar acceso en: https://manager.westforce.com.au')
