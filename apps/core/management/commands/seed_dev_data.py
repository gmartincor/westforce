from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from apps.core.services.seeders import DevDataSeeder


from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Seeds development database with realistic test data for Australian removals company'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Delete all existing data before seeding'
        )
        parser.add_argument(
            '--users',
            action='store_true',
            help='Seed only user data'
        )
        parser.add_argument(
            '--categories',
            action='store_true',
            help='Seed only expense categories'
        )
        parser.add_argument(
            '--company',
            action='store_true',
            help='Seed only company data'
        )
        parser.add_argument(
            '--invoices',
            action='store_true',
            help='Seed only invoices'
        )
        parser.add_argument(
            '--transactions',
            action='store_true',
            help='Seed income and expense transactions'
        )

    def handle(self, *args, **options):
        if not settings.DEBUG and settings.ENVIRONMENT == 'production':
            self.stdout.write(
                self.style.ERROR('❌ Cannot seed data in production environment')
            )
            return

        self.stdout.write('🌱 SEEDING DEVELOPMENT DATA')
        self.stdout.write('='*60)

        try:
            with transaction.atomic():
                seeder = DevDataSeeder(stdout=self.stdout, style=self.style)

                if options['flush']:
                    seeder.flush_all_data()

                has_specific_flag = any([
                    options['users'],
                    options['categories'],
                    options['company'],
                    options['invoices'],
                    options['transactions']
                ])

                if options['users']:
                    seeder.seed_users()
                if options['categories']:
                    seeder.seed_expense_categories()
                if options['company']:
                    seeder.seed_company()
                if options['invoices']:
                    seeder.seed_invoices()
                if options['transactions']:
                    seeder.seed_incomes()
                    seeder.seed_expenses()
                
                if not has_specific_flag:
                    seeder.seed_all()

                self.stdout.write('')
                self.stdout.write(self.style.SUCCESS('✅ SEEDING COMPLETED'))
                self.stdout.write('='*60)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error during seeding: {str(e)}')
            )
            raise
