from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create test users for Westforce Removals Company'

    def handle(self, *args, **options):
        # Delete existing users first
        User.objects.all().delete()
        
        # Create admin user
        admin = User.objects.create_user(
            username='admin',
            email='admin@westforce.com.au',
            first_name='System',
            last_name='Administrator',
            password='admin123',
            position='System Administrator'
        )
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()
        
        # Create operations manager
        manager = User.objects.create_user(
            username='james.turner',
            email='james.turner@westforce.com.au',
            first_name='James',
            last_name='Turner',
            password='manager123',
            position='Operations Manager',
            phone='+61 8 9123 4567'
        )
        
        # Create finance coordinator
        finance = User.objects.create_user(
            username='sarah.mitchell',
            email='sarah.mitchell@westforce.com.au',
            first_name='Sarah',
            last_name='Mitchell',
            password='finance123',
            position='Finance Coordinator',
            phone='+61 8 9123 4568'
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created users for Westforce Removals Company:\n'
                f'- admin (password: admin123) - System Administrator\n'
                f'- james.turner (password: manager123) - Operations Manager\n'
                f'- sarah.mitchell (password: finance123) - Finance Coordinator'
            )
        )
