from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from apps.core.services.seeders import YearlyTransactionSeeder, YearlyInvoiceSeeder


class Command(BaseCommand):
    help = 'Seeds database with realistic data for all months of 2025'

    def add_arguments(self, parser):
        parser.add_argument(
            '--transactions-only',
            action='store_true',
            help='Seed only transactions (incomes and expenses)'
        )
        parser.add_argument(
            '--invoices-only',
            action='store_true',
            help='Seed only invoices'
        )

    def handle(self, *args, **options):
        if not settings.DEBUG and settings.ENVIRONMENT == 'production':
            self.stdout.write(
                self.style.ERROR('❌ Cannot seed data in production environment')
            )
            return

        self.stdout.write('🌱 SEEDING 2025 YEARLY DATA')
        self.stdout.write('='*60)

        try:
            with transaction.atomic():
                if options['transactions_only']:
                    seeder = YearlyTransactionSeeder(stdout=self.stdout, style=self.style)
                    seeder.seed()
                elif options['invoices_only']:
                    seeder = YearlyInvoiceSeeder(stdout=self.stdout, style=self.style)
                    seeder.seed()
                else:
                    transaction_seeder = YearlyTransactionSeeder(stdout=self.stdout, style=self.style)
                    transaction_seeder.seed()
                    
                    invoice_seeder = YearlyInvoiceSeeder(stdout=self.stdout, style=self.style)
                    invoice_seeder.seed()

                self.stdout.write('')
                self.stdout.write(self.style.SUCCESS('✅ YEARLY SEEDING COMPLETED'))
                self.stdout.write('='*60)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error during seeding: {str(e)}')
            )
            raise
