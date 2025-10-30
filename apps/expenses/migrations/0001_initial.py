import apps.expenses.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ExpenseCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created date')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified date')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Name')),
                ('slug', models.SlugField(max_length=100, unique=True, verbose_name='Slug')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('category_type', models.CharField(
                    choices=[
                        ('FIXED', 'Fixed'),
                        ('VARIABLE', 'Variable'),
                        ('TAX', 'Tax'),
                        ('OCCASIONAL', 'Occasional')
                    ],
                    max_length=20,
                    verbose_name='Category type'
                )),
                ('is_active', models.BooleanField(db_index=True, default=True, verbose_name='Active')),
            ],
            options={
                'verbose_name': 'Expense category',
                'verbose_name_plural': 'Expense categories',
                'db_table': 'expense_categories',
                'ordering': ['category_type', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created date')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified date')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Amount')),
                ('date', models.DateField(verbose_name='Date')),
                ('description', models.TextField(verbose_name='Description')),
                ('accounting_year', models.PositiveIntegerField(db_index=True, verbose_name='Accounting year')),
                ('accounting_month', models.PositiveSmallIntegerField(db_index=True, verbose_name='Accounting month')),
                ('invoice_number', models.CharField(blank=True, max_length=100, verbose_name='Invoice number')),
                ('attachment', models.FileField(
                    blank=True,
                    null=True,
                    upload_to=apps.expenses.models.expense_attachment_path,
                    verbose_name='Attachment'
                )),
                ('category', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='expenses',
                    to='expenses.expensecategory',
                    verbose_name='Category'
                )),
            ],
            options={
                'verbose_name': 'Expense',
                'verbose_name_plural': 'Expenses',
                'db_table': 'expenses',
                'ordering': ['-date', '-created'],
            },
        ),
        migrations.AddIndex(
            model_name='expensecategory',
            index=models.Index(fields=['category_type', 'is_active'], name='expense_cat_categor_b516e7_idx'),
        ),
        migrations.AddIndex(
            model_name='expense',
            index=models.Index(fields=['accounting_year', 'accounting_month'], name='expenses_account_193753_idx'),
        ),
        migrations.AddIndex(
            model_name='expense',
            index=models.Index(fields=['category', 'date'], name='expenses_categor_99cf21_idx'),
        ),
        migrations.AddIndex(
            model_name='expense',
            index=models.Index(fields=['date'], name='expenses_date_a77b87_idx'),
        ),
        migrations.AddIndex(
            model_name='expense',
            index=models.Index(fields=['accounting_year', 'category'], name='expenses_account_c7338d_idx'),
        ),
    ]
