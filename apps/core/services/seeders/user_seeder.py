from django.contrib.auth import get_user_model
from .base_seeder import BaseSeeder

User = get_user_model()


class UserSeeder(BaseSeeder):
    
    def seed(self) -> None:
        self.log_info('Seeding users...')
        
        if User.objects.exists():
            self.log_info('Users already exist. Skipping.')
            return
        
        manager = User.objects.create_superuser(
            username='admin',
            email='admin@westforce.com.au',
            password='admin123',
            first_name='Westforce',
            last_name='Admin',
            phone='(08) 9123 4567',
            position='General Manager',
            company_name='Westforce Moving Company'
        )
        
        self.log_success(f'Created manager user: {manager.username}')
        self.log_info(f'Login credentials -> username: admin, password: admin123')
