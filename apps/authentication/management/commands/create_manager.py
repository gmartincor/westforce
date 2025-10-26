from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.exceptions import ValidationError
import getpass

User = get_user_model()


class Command(BaseCommand):
    help = 'Create the single manager user for Westforce'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username for the manager')
        parser.add_argument('--email', type=str, help='Email for the manager')
        parser.add_argument('--company-name', type=str, help='Company name', default='Westforce Moving Company')

    def handle(self, *args, **options):
        username = options.get('username') or input('Username: ')
        email = options.get('email') or input('Email: ')
        first_name = input('First name: ')
        last_name = input('Last name: ')
        phone = input('Phone (optional): ')
        position = input('Position (optional): ')
        company_name = options.get('company_name') or input(f'Company name [Westforce Moving Company]: ') or 'Westforce Moving Company'
        
        password = getpass.getpass('Password: ')
        password_confirm = getpass.getpass('Confirm password: ')
        
        if password != password_confirm:
            self.stdout.write(self.style.ERROR('Passwords do not match'))
            return

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    position=position,
                    company_name=company_name,
                    is_staff=True,
                    is_superuser=True,
                    is_active=True
                )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully created manager user: {user.username} for {getattr(user, "company_name", "Company")}'
                    )
                )
                
        except ValidationError as e:
            self.stdout.write(self.style.ERROR(f'Validation error: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating user: {e}'))
