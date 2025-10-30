import apps.invoicing.validators
import datetime
from decimal import Decimal
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created date')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified date')),
                ('legal_form', models.CharField(
                    choices=[
                        ('SOLE_TRADER', 'Sole Trader'),
                        ('PTY_LTD', 'Proprietary Limited Company (Pty Ltd)'),
                        ('PUBLIC_COMPANY', 'Public Company Limited'),
                        ('PARTNERSHIP', 'Partnership'),
                        ('TRUST', 'Trust')
                    ],
                    max_length=20,
                    verbose_name='Legal structure'
                )),
                ('business_name', models.CharField(max_length=200, verbose_name='Business name')),
                ('legal_name', models.CharField(blank=True, max_length=200, verbose_name='Legal name')),
                ('abn', models.CharField(
                    help_text='Australian Business Number (11 digits)',
                    max_length=14,
                    validators=[apps.invoicing.validators.ABNValidator()],
                    verbose_name='ABN'
                )),
                ('acn', models.CharField(
                    blank=True,
                    help_text='Australian Company Number (9 digits, required for companies)',
                    max_length=11,
                    validators=[apps.invoicing.validators.ACNValidator()],
                    verbose_name='ACN'
                )),
                ('gst_registered', models.BooleanField(
                    default=True,
                    help_text='Is the business registered for GST?',
                    verbose_name='GST registered'
                )),
                ('address', models.TextField(verbose_name='Street address')),
                ('postal_code', models.CharField(
                    max_length=4,
                    validators=[apps.invoicing.validators.AustralianPostcodeValidator()],
                    verbose_name='Postcode'
                )),
                ('city', models.CharField(max_length=100, verbose_name='Suburb')),
                ('state', models.CharField(
                    choices=[
                        ('NSW', 'New South Wales'),
                        ('VIC', 'Victoria'),
                        ('QLD', 'Queensland'),
                        ('WA', 'Western Australia'),
                        ('SA', 'South Australia'),
                        ('TAS', 'Tasmania'),
                        ('ACT', 'Australian Capital Territory'),
                        ('NT', 'Northern Territory')
                    ],
                    max_length=3,
                    verbose_name='State/Territory'
                )),
                ('phone', models.CharField(
                    blank=True,
                    help_text='Format: (02) 1234 5678 or 0412 345 678',
                    max_length=20,
                    verbose_name='Phone'
                )),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='Email')),
                ('website', models.URLField(blank=True, verbose_name='Website')),
                ('bank_name', models.CharField(max_length=100, verbose_name='Bank name')),
                ('bsb', models.CharField(
                    help_text='Bank-State-Branch number',
                    max_length=7,
                    validators=[apps.invoicing.validators.BSBValidator()],
                    verbose_name='BSB'
                )),
                ('account_number', models.CharField(
                    max_length=10,
                    validators=[apps.invoicing.validators.AustralianAccountNumberValidator()],
                    verbose_name='Account number'
                )),
                ('invoice_prefix', models.CharField(default='INV', max_length=10, verbose_name='Invoice prefix')),
                ('current_number', models.IntegerField(
                    default=0,
                    validators=[django.core.validators.MinValueValidator(0)]
                )),
                ('logo', models.ImageField(blank=True, null=True, upload_to='company/logos/')),
            ],
            options={
                'verbose_name_plural': 'Companies',
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created date')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified date')),
                ('reference', models.CharField(blank=True, max_length=50, null=True, unique=True, db_index=True)),
                ('issue_date', models.DateField(default=datetime.date.today, verbose_name='Issue date', db_index=True)),
                ('due_date', models.DateField(
                    blank=True,
                    help_text='Calculated from issue date and payment terms',
                    null=True,
                    verbose_name='Due date',
                    db_index=True
                )),
                ('client_type', models.CharField(
                    choices=[
                        ('BUSINESS', 'Business (ABN holder)'),
                        ('INDIVIDUAL', 'Individual')
                    ],
                    max_length=20,
                    verbose_name='Client type'
                )),
                ('client_name', models.CharField(max_length=200, verbose_name='Client name', db_index=True)),
                ('client_abn', models.CharField(
                    blank=True,
                    help_text='Required for business clients',
                    max_length=14,
                    verbose_name='Client ABN',
                    db_index=True
                )),
                ('client_address', models.TextField(verbose_name='Client address')),
                ('status', models.CharField(
                    choices=[
                        ('DRAFT', 'Draft'),
                        ('SENT', 'Sent'),
                        ('PAID', 'Paid'),
                        ('OVERDUE', 'Overdue'),
                        ('CANCELLED', 'Cancelled')
                    ],
                    default='DRAFT',
                    max_length=20,
                    verbose_name='Status',
                    db_index=True
                )),
                ('payment_terms', models.TextField(
                    default='Payment due within 30 days',
                    verbose_name='Payment terms'
                )),
                ('payment_reference', models.CharField(
                    blank=True,
                    help_text='Generated reference for bank reconciliation',
                    max_length=100,
                    verbose_name='Payment reference'
                )),
                ('payment_date', models.DateField(blank=True, null=True, verbose_name='Payment date')),
                ('notes', models.TextField(
                    blank=True,
                    help_text='Internal notes (not shown on invoice)',
                    verbose_name='Additional notes'
                )),
                ('pdf_file', models.FileField(blank=True, upload_to='invoices/pdfs/')),
                ('retention_date', models.DateField(
                    blank=True,
                    editable=False,
                    help_text='ATO requires 5 years retention',
                    null=True,
                    verbose_name='Retention until'
                )),
                ('company', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='invoicing.company',
                    db_index=True
                )),
            ],
            options={
                'verbose_name': 'Invoice',
                'verbose_name_plural': 'Invoices',
                'ordering': ['-issue_date', '-id'],
            },
        ),
        migrations.CreateModel(
            name='InvoiceItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(verbose_name='Description')),
                ('quantity', models.PositiveIntegerField(default=1, verbose_name='Quantity')),
                ('unit_price', models.DecimalField(
                    decimal_places=2,
                    max_digits=10,
                    validators=[django.core.validators.MinValueValidator(Decimal('0.01'))],
                    verbose_name='Unit price (ex GST)'
                )),
                ('gst_treatment', models.CharField(
                    choices=[
                        ('TAXABLE', 'Taxable (10% GST)'),
                        ('GST_FREE', 'GST-free (health, education, exports)'),
                        ('INPUT_TAXED', 'Input taxed (financial supplies, residential rent)')
                    ],
                    default='TAXABLE',
                    help_text='How GST applies to this item',
                    max_length=20,
                    verbose_name='GST treatment'
                )),
                ('invoice', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='items',
                    to='invoicing.invoice',
                    db_index=True
                )),
            ],
            options={
                'verbose_name': 'Invoice item',
                'verbose_name_plural': 'Invoice items',
            },
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['company', 'status'], name='invoicing_i_company_status_idx'),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['issue_date', 'status'], name='invoicing_i_issue_status_idx'),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['client_abn', 'status'], name='invoicing_i_abn_status_idx'),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['-issue_date', '-id'], name='invoicing_i_issue_id_desc_idx'),
        ),
        migrations.AddIndex(
            model_name='company',
            index=models.Index(fields=['abn'], name='invoicing_c_abn_idx'),
        ),
        migrations.AddConstraint(
            model_name='invoice',
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(client_type='INDIVIDUAL') | models.Q(client_abn__gt=''),
                ),
                name='client_abn_required_for_business'
            ),
        ),
        migrations.AddConstraint(
            model_name='invoice',
            constraint=models.CheckConstraint(
                check=models.Q(due_date__gte=models.F('issue_date')),
                name='due_date_after_issue_date'
            ),
        ),
        migrations.AddConstraint(
            model_name='invoiceitem',
            constraint=models.CheckConstraint(
                check=models.Q(quantity__gt=0),
                name='quantity_positive'
            ),
        ),
        migrations.AddConstraint(
            model_name='invoiceitem',
            constraint=models.CheckConstraint(
                check=models.Q(unit_price__gt=0),
                name='unit_price_positive'
            ),
        ),
        migrations.AddConstraint(
            model_name='company',
            constraint=models.CheckConstraint(
                check=models.Q(current_number__gte=0),
                name='current_number_non_negative'
            ),
        ),
    ]
