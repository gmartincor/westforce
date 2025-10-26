from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.conf import settings
import os

User = get_user_model()


class Command(BaseCommand):
    help = 'Cleans the database of all test data to prepare for production'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to delete all test data',
        )
        parser.add_argument(
            '--environment',
            type=str,
            default='development',
            help='Specify the environment (development/production)',
        )

    def handle(self, *args, **options):
        if not options.get('confirm', False):
            self.stdout.write(
                self.style.ERROR('⚠️  WARNING: This command will delete ALL test data.')
            )
            self.stdout.write(
                self.style.ERROR('To confirm, run: python manage.py cleanup_production --confirm')
            )
            return

        environment = options.get('environment', 'development')
        
        if environment == 'production' and settings.DEBUG:
            self.stdout.write(
                self.style.ERROR('❌ Cannot run production cleanup with DEBUG=True')
            )
            return

        self.stdout.write('🧹 Starting test data cleanup...')
        
        try:
            with transaction.atomic():
                self._cleanup_test_users()
                self._cleanup_test_income_records()
                self._cleanup_test_business_lines()
                self._cleanup_test_expenses()
                
            self.stdout.write(self.style.SUCCESS('✅ Cleanup completed successfully'))
            self.stdout.write('')
            self.stdout.write('📋 DATABASE READY FOR PRODUCTION')
            self.stdout.write('='*50)
            self.stdout.write('• Test income records deleted')
            self.stdout.write('• Test business lines deleted')
            self.stdout.write('• Test expenses deleted')
            self.stdout.write('')
            self.stdout.write('⚠️  IMPORTANT: Run migrations before the first deploy:')
            self.stdout.write('   python manage.py migrate')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error during cleanup: {str(e)}')
            )

    def _cleanup_test_users(self):
        """Deletes test users but keeps auth structure"""
        self.stdout.write('🔄 Cleaning up test users...')
        
        # Delete specific test users (keep superusers in development)
        test_usernames = ['maria.glow', 'carlos.glow', 'admin']
        
        # In production, delete all except if there are existing superusers
        if not settings.DEBUG:
            User.objects.filter(username__in=test_usernames).delete()
            self.stdout.write('   ✓ Test users deleted')
        else:
            self.stdout.write('   ⚠️  Development mode: users kept')

    def _cleanup_test_income_records(self):
        """Deletes test income records"""
        self.stdout.write('🔄 Cleaning up test income records...')
        
        try:
            from apps.accounting.models import Income
            
            # Identify test income records by common patterns
            test_patterns = [
                'test', 'prueba', 'ejemplo', 'demo', 'ficticio'
            ]
            
            deleted_incomes = 0
            
            for pattern in test_patterns:
                # Delete test income records
                incomes = Income.objects.filter(
                    client_name__icontains=pattern
                ) | Income.objects.filter(
                    description__icontains=pattern
                ) | Income.objects.filter(
                    reference_number__icontains=pattern
                )
                
                deleted_incomes += incomes.count()
                incomes.delete()
            
            self.stdout.write(f'   ✓ {deleted_incomes} test income records deleted')
            
        except ImportError:
            self.stdout.write('   ⚠️  Accounting module not available')

    def _cleanup_test_business_lines(self):
        """Deletes test business lines"""
        self.stdout.write('🔄 Cleaning up test business lines...')
        
        try:
            from apps.business_lines.models import BusinessLine
            
            # Only delete lines clearly marked as test
            test_lines = BusinessLine.objects.filter(
                name__icontains='test'
            ) | BusinessLine.objects.filter(
                name__icontains='prueba'
            )
            
            deleted_count = test_lines.count()
            test_lines.delete()
            
            self.stdout.write(f'   ✓ {deleted_count} test business lines deleted')
            
        except ImportError:
            self.stdout.write('   ⚠️  Business_lines module not available')

    def _cleanup_test_expenses(self):
        """Deletes test expenses"""
        self.stdout.write('🔄 Cleaning up test expenses...')
        
        try:
            from apps.expenses.models import Expense, ExpenseCategory
            
            # Delete expenses with test descriptions
            test_expenses = Expense.objects.filter(
                description__icontains='test'
            ) | Expense.objects.filter(
                description__icontains='prueba'
            )
            
            deleted_expenses = test_expenses.count()
            test_expenses.delete()
            
            # Delete test categories
            test_categories = ExpenseCategory.objects.filter(
                name__icontains='test'
            ) | ExpenseCategory.objects.filter(
                name__icontains='prueba'
            )
            
            deleted_categories = test_categories.count()
            test_categories.delete()
            
            self.stdout.write(f'   ✓ {deleted_expenses} expenses and {deleted_categories} categories deleted')
            
        except ImportError:
            self.stdout.write('   ⚠️  Expenses module not available')
