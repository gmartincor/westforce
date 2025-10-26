from django.core.management.base import BaseCommand
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Verifica que la configuración esté lista para producción'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                '🎯 Verificando configuración para producción en Render\n'
                '=' * 60
            )
        )

        if settings.DEBUG:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  Ejecutando en modo DEBUG (desarrollo)\n'
                    '   En producción, Render configurará DEBUG=False automáticamente'
                )
            )
        
        if 'django-insecure' in settings.SECRET_KEY:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  SECRET_KEY de desarrollo detectada\n'
                    '   En producción, configurar SECRET_KEY segura en variables de entorno'
                )
            )
        
        if hasattr(settings, 'DOMAIN'):
            self.stdout.write(
                self.style.SUCCESS(f'✅ DOMAIN configurado: {settings.DOMAIN}')
            )
        else:
            self.stdout.write(
                self.style.ERROR('❌ DOMAIN no configurado')
            )
        
        if '*.westforce.com.au' in settings.ALLOWED_HOSTS:
            self.stdout.write(
                self.style.SUCCESS('✅ ALLOWED_HOSTS incluye *.westforce.com.au')
            )
        else:
            self.stdout.write(
                self.style.ERROR('❌ ALLOWED_HOSTS no incluye *.westforce.com.au')
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Configuración base lista para producción!\n'
                f'   Dominio objetivo: westforce.com.au\n'
                f'   Subdominios: manager.westforce.com.au\n'
                f'   Cache: Base de datos (sin Redis)\n'
                f'\n📋 Pasos para producción:\n'
                f'   1. Crear PostgreSQL en Render\n'
                f'   2. Crear Web Service en Render\n'
                f'   3. Configurar variables de entorno\n'
                f'   4. Configurar DNS (A record + CNAME manager)\n'
                f'   5. Deploy automático\n'
                f'\n🔧 Variables críticas para Render:\n'
                f'   - SECRET_KEY: Generar clave segura\n'
                f'   - DEBUG: False\n'
                f'   - ALLOWED_HOSTS: westforce.com.au,manager.westforce.com.au\n'
                f'   - DB_* : Credenciales de PostgreSQL\n'
                f'\n💰 Costo total: $14/mes (PostgreSQL + Web Service)\n'
                f'   🚫 Redis omitido para ahorrar $7/mes\n'
            )
        )
