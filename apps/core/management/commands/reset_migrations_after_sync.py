from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
import sys


class Command(BaseCommand):
    help = 'Resetea migraciones después de sincronizar con producción'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fake-initial',
            action='store_true',
            help='Marcar migraciones iniciales como fake',
        )
        parser.add_argument(
            '--list-migrations',
            action='store_true',
            help='Solo listar estado de migraciones',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔄 RESETEO DE MIGRACIONES POST-SINCRONIZACIÓN'))
        self.stdout.write('=' * 60)

        if options['list_migrations']:
            self.list_migrations()
            return

        try:
            from django.conf import settings
            if not settings.DEBUG:
                self.stdout.write(
                    self.style.ERROR('❌ Este comando solo debe ejecutarse en desarrollo (DEBUG=True)')
                )
                sys.exit(1)

            self.stdout.write('\n📋 Estado actual de migraciones:')
            self.list_migrations()

            confirm = input('\n¿Continuar con el reseteo de migraciones? (y/N): ')
            if confirm.lower() != 'y':
                self.stdout.write(self.style.WARNING('❌ Operación cancelada'))
                return

            self.stdout.write('\n🔄 Reseteando migraciones...')
            self.reset_migrations()

            self.stdout.write(self.style.SUCCESS('\n✅ Reseteo de migraciones completado'))
            self.stdout.write('\n🚀 Próximos pasos:')
            self.stdout.write('   1. Verificar que la app funciona correctamente')
            self.stdout.write('   2. Crear nuevas migraciones si es necesario')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error durante el reseteo: {str(e)}')
            )
            sys.exit(1)

    def list_migrations(self):
        try:
            call_command('showmigrations', verbosity=1)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error al listar migraciones: {str(e)}')
            )

    def reset_migrations(self):
        try:
            call_command('migrate', '--fake', verbosity=1)
            self.stdout.write(self.style.SUCCESS('✅ Migraciones reseteadas'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠️  Advertencia en migraciones: {str(e)}'))

        self.stdout.write('\n📊 Estado final de migraciones:')
        self.list_migrations()

    def check_database_tables(self):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            
            self.stdout.write('\n📋 Tablas en la base de datos:')
            for table in tables:
                self.stdout.write(f'   • {table[0]}')
