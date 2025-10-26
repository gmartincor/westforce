from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea el usuario único del sistema'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Nombre de usuario')
        parser.add_argument('--email', type=str, help='Email del usuario')
        parser.add_argument('--password', type=str, help='Contraseña')
        parser.add_argument('--first-name', type=str, help='Nombre')
        parser.add_argument('--last-name', type=str, help='Apellidos')
        parser.add_argument('--force', action='store_true', help='Forzar creación eliminando otros usuarios')
        parser.add_argument('--interactive', action='store_true', help='Modo interactivo')

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                self._handle_command(options)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error inesperado: {e}')
            )

    def _handle_command(self, options):
        force = options.get('force', False)
        interactive = options.get('interactive', False)

        if User.objects.exists() and not force:
            self.stdout.write(
                self.style.WARNING(
                    'Ya existe un usuario en el sistema.'
                )
            )
            self.stdout.write(
                'Use --force para reemplazarlo o --interactive para gestionar usuarios.'
            )
            return

        if force and User.objects.exists():
            user_count = User.objects.count()
            self.stdout.write(f'Eliminando {user_count} usuario(s) existente(s)...')
            User.objects.all().delete()
            self.stdout.write(self.style.WARNING('Usuarios eliminados'))

        user_data = self._collect_user_data(options, interactive)
        
        if not self._validate_required_fields(user_data):
            return

        try:
            user = self._create_user(user_data)
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Usuario único creado exitosamente: {user.username} ({user.email})'
                )
            )
            self.stdout.write('')
            self.stdout.write('🔑 CREDENCIALES DE ACCESO:')
            self.stdout.write(f'   Usuario: {user.username}')
            self.stdout.write(f'   Email: {user.email}')
            self.stdout.write('   Contraseña: [la que configuraste]')
            self.stdout.write('')
            self.stdout.write('🌐 Acceso web:')
            self.stdout.write('   http://localhost:8000/auth/login/')
            
        except ValidationError as e:
            self.stdout.write(
                self.style.ERROR(f'Error de validación: {e}')
            )

    def _collect_user_data(self, options, interactive):
        user_data = {}
        
        fields = ['username', 'email', 'password', 'first_name', 'last_name']
        field_labels = {
            'username': 'Nombre de usuario',
            'email': 'Email',
            'password': 'Contraseña',
            'first_name': 'Nombre',
            'last_name': 'Apellidos'
        }
        
        for field in fields:
            option_key = field.replace('_', '-') if '_' in field else field
            value = options.get(option_key)
            
            if not value and interactive:
                label = field_labels[field]
                if field == 'password':
                    import getpass
                    value = getpass.getpass(f'{label}: ')
                else:
                    value = input(f'{label}: ')
            
            user_data[field] = value or ''
        
        return user_data

    def _validate_required_fields(self, user_data):
        required_fields = ['username', 'email', 'password']
        missing_fields = [field for field in required_fields if not user_data.get(field)]
        
        if missing_fields:
            self.stdout.write(
                self.style.ERROR(
                    f'Campos requeridos faltantes: {", ".join(missing_fields)}'
                )
            )
            self.stdout.write('Use --interactive para modo interactivo')
            return False
        
        return True

    def _create_user(self, user_data):
        return User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            is_staff=True,
            is_superuser=True,
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', '')
        )
