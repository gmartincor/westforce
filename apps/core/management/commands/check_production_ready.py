from django.core.management.base import BaseCommand
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Checks if the configuration is ready for production'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                '🎯 Checking configuration for production\n'
                '=' * 60
            )
        )

        errors = 0
        warnings = 0

        # DEBUG check
        if settings.DEBUG:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  Running in DEBUG mode (development)\n'
                    '   In production, DEBUG must be False'
                )
            )
            warnings += 1
        else:
            self.stdout.write(self.style.SUCCESS('✅ DEBUG=False'))
        
        # SECRET_KEY check
        if 'django-insecure' in settings.SECRET_KEY:
            self.stdout.write(
                self.style.ERROR(
                    '❌ Development SECRET_KEY detected\n'
                    '   Configure a secure SECRET_KEY in environment variables'
                )
            )
            errors += 1
        else:
            self.stdout.write(self.style.SUCCESS('✅ Secure SECRET_KEY configured'))
        
        # DOMAIN check
        if hasattr(settings, 'DOMAIN') and settings.DOMAIN:
            self.stdout.write(
                self.style.SUCCESS(f'✅ DOMAIN configured: {settings.DOMAIN}')
            )
        else:
            self.stdout.write(
                self.style.WARNING('⚠️  DOMAIN not configured')
            )
            warnings += 1
        
        # ALLOWED_HOSTS check
        if settings.ALLOWED_HOSTS:
            self.stdout.write(
                self.style.SUCCESS(f'✅ ALLOWED_HOSTS: {", ".join(settings.ALLOWED_HOSTS)}')
            )
        else:
            self.stdout.write(
                self.style.ERROR('❌ ALLOWED_HOSTS is empty')
            )
            errors += 1
        
        # SSL/Security checks
        security_settings = [
            ('SECURE_SSL_REDIRECT', True),
            ('SECURE_HSTS_SECONDS', 31536000),
            ('SESSION_COOKIE_SECURE', True),
            ('CSRF_COOKIE_SECURE', True),
        ]
        
        for setting_name, expected_value in security_settings:
            actual = getattr(settings, setting_name, None)
            if actual and (actual == expected_value or (isinstance(expected_value, int) and actual >= expected_value)):
                self.stdout.write(self.style.SUCCESS(f'✅ {setting_name} configured'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠️  {setting_name} not properly configured'))
                warnings += 1

        # Summary
        self.stdout.write('\n' + '=' * 60)
        if errors == 0 and warnings == 0:
            self.stdout.write(
                self.style.SUCCESS('🎉 Configuration is ready for production!')
            )
        elif errors == 0:
            self.stdout.write(
                self.style.WARNING(f'⚠️  {warnings} warning(s). Review before deploying.')
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ {errors} error(s) and {warnings} warning(s). Fix before deploying.')
            )
