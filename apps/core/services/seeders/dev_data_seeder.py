from django.contrib.auth import get_user_model
from apps.expenses.models import ExpenseCategory, Expense
from apps.accounting.models import Income
from apps.invoicing.models import Company, Invoice, InvoiceItem
from .base_seeder import BaseSeeder
from .user_seeder import UserSeeder
from .category_seeder import CategorySeeder
from .company_seeder import CompanySeeder
from .transaction_seeder import TransactionSeeder
from .invoice_seeder import InvoiceSeeder

User = get_user_model()


class DevDataSeeder(BaseSeeder):
    
    def __init__(self, stdout=None, style=None):
        super().__init__(stdout, style)
        self.user_seeder = UserSeeder(stdout, style)
        self.category_seeder = CategorySeeder(stdout, style)
        self.company_seeder = CompanySeeder(stdout, style)
        self.transaction_seeder = TransactionSeeder(stdout, style)
        self.invoice_seeder = InvoiceSeeder(stdout, style)
    
    def seed(self) -> None:
        self.seed_all()
    
    def seed_all(self) -> None:
        self.seed_users()
        self.seed_expense_categories()
        self.seed_company()
        self.seed_invoices()
        self.seed_incomes()
        self.seed_expenses()
    
    def seed_users(self) -> None:
        self.user_seeder.seed()
    
    def seed_expense_categories(self) -> None:
        self.category_seeder.seed()
    
    def seed_company(self) -> None:
        self.company_seeder.seed()
    
    def seed_invoices(self) -> None:
        self.invoice_seeder.seed()
    
    def seed_incomes(self) -> None:
        self.transaction_seeder.seed_incomes()
    
    def seed_expenses(self) -> None:
        self.transaction_seeder.seed_expenses()
    
    def flush_all_data(self) -> None:
        self.log_info('Flushing all data...')
        
        InvoiceItem.objects.all().delete()
        Invoice.objects.all().delete()
        Income.objects.all().delete()
        Expense.objects.all().delete()
        ExpenseCategory.objects.all().delete()
        Company.objects.all().delete()
        User.objects.all().delete()
        
        self.log_success('All data flushed')
