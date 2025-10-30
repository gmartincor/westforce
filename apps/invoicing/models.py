from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date

from apps.core.models import TimeStampedModel
from .constants import (
    LEGAL_FORMS, CLIENT_TYPES, INVOICE_STATUS, GST_RATE_CHOICES,
    AUSTRALIAN_STATES, GST_RATE, TAX_INVOICE_THRESHOLD, GST_TREATMENT,
    RECORD_RETENTION_YEARS, GST_FREE_RATE
)
from .validators import (
    AustralianBusinessValidator, AustralianPostcodeValidator,
    BSBValidator, ABNValidator, ACNValidator, AustralianAccountNumberValidator
)


class Company(TimeStampedModel):
    legal_form = models.CharField(
        max_length=20,
        choices=LEGAL_FORMS,
        verbose_name="Legal structure"
    )
    business_name = models.CharField(max_length=200, verbose_name="Business name")
    legal_name = models.CharField(max_length=200, blank=True, verbose_name="Legal name")
    
    abn = models.CharField(
        max_length=14,
        verbose_name="ABN",
        validators=[ABNValidator()],
        help_text='Australian Business Number (11 digits)'
    )
    acn = models.CharField(
        max_length=11,
        blank=True,
        verbose_name="ACN",
        validators=[ACNValidator()],
        help_text='Australian Company Number (9 digits, required for companies)'
    )
    
    gst_registered = models.BooleanField(
        default=True,
        verbose_name="GST registered",
        help_text="Is the business registered for GST?"
    )
    
    address = models.TextField(verbose_name="Street address")
    postal_code = models.CharField(
        max_length=4,
        verbose_name="Postcode",
        validators=[AustralianPostcodeValidator()]
    )
    city = models.CharField(max_length=100, verbose_name="Suburb")
    state = models.CharField(
        max_length=3,
        choices=AUSTRALIAN_STATES,
        verbose_name="State/Territory"
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Phone",
        help_text='Format: (02) 1234 5678 or 0412 345 678'
    )
    email = models.EmailField(blank=True, verbose_name="Email")
    website = models.URLField(blank=True, verbose_name="Website")
    
    bank_name = models.CharField(max_length=100, verbose_name="Bank name")
    bsb = models.CharField(
        max_length=7,
        verbose_name="BSB",
        validators=[BSBValidator()],
        help_text='Bank-State-Branch number'
    )
    account_number = models.CharField(
        max_length=10,
        verbose_name="Account number",
        validators=[AustralianAccountNumberValidator()],
    )
    
    invoice_prefix = models.CharField(
        max_length=10,
        default="INV",
        verbose_name="Invoice prefix"
    )
    current_number = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    logo = models.ImageField(upload_to='company/logos/', blank=True, null=True)

    def clean(self):
        super().clean()
        if self.legal_form in ['PTY_LTD', 'PUBLIC_COMPANY'] and not self.acn:
            raise ValidationError({
                'acn': 'ACN is required for Proprietary Limited and Public companies'
            })
        
        if self.abn:
            self.abn = AustralianBusinessValidator.validate_abn(self.abn)

    def get_formatted_abn(self):
        return AustralianBusinessValidator.format_abn(self.abn)

    def get_formatted_acn(self):
        if not self.acn:
            return ''
        return AustralianBusinessValidator.format_acn(self.acn)

    def get_formatted_bsb(self):
        return AustralianBusinessValidator.format_bsb(self.bsb)

    def get_full_address(self):
        return f"{self.address}, {self.city} {self.state} {self.postal_code}"

    def get_display_name(self):
        return self.legal_name or self.business_name

    @property
    def is_sole_trader(self):
        return self.legal_form == 'SOLE_TRADER'

    def __str__(self):
        return self.business_name

    class Meta:
        verbose_name_plural = "Companies"
        indexes = [
            models.Index(fields=['abn'], name='invoicing_c_abn_idx'),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(current_number__gte=0),
                name='current_number_non_negative'
            ),
        ]


class Invoice(TimeStampedModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, db_index=True)
    reference = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        db_index=True
    )
    issue_date = models.DateField(default=date.today, verbose_name="Issue date", db_index=True)
    due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Due date",
        help_text='Calculated from issue date and payment terms',
        db_index=True
    )
    
    client_type = models.CharField(
        max_length=20,
        choices=CLIENT_TYPES,
        verbose_name="Client type"
    )
    client_name = models.CharField(max_length=200, verbose_name="Client name", db_index=True)
    client_abn = models.CharField(
        max_length=14,
        blank=True,
        verbose_name="Client ABN",
        help_text='Required for business clients',
        db_index=True
    )
    client_address = models.TextField(verbose_name="Client address")
    
    status = models.CharField(
        max_length=20,
        choices=INVOICE_STATUS,
        default='DRAFT',
        verbose_name="Status",
        db_index=True
    )
    payment_terms = models.TextField(
        default="Payment due within 30 days",
        verbose_name="Payment terms"
    )
    payment_reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Payment reference",
        help_text='Generated reference for bank reconciliation'
    )
    payment_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Payment date"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Additional notes",
        help_text='Internal notes (not shown on invoice)'
    )
    pdf_file = models.FileField(upload_to='invoices/pdfs/', blank=True)
    retention_date = models.DateField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="Retention until",
        help_text=f'ATO requires {RECORD_RETENTION_YEARS} years retention'
    )

    @property
    def subtotal(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def gst_amount(self):
        return sum(item.gst_amount for item in self.items.all())

    @property
    def total_amount(self):
        return self.subtotal + self.gst_amount

    @property
    def is_tax_invoice(self):
        return self.company.gst_registered and self.total_amount >= TAX_INVOICE_THRESHOLD

    def generate_reference(self):
        if not self.issue_date:
            self.issue_date = date.today()
        year = self.issue_date.year % 100
        
        from django.db import transaction
        with transaction.atomic():
            company = Company.objects.select_for_update().get(pk=self.company.pk)
            company.current_number += 1
            company.save()
            return f"{company.invoice_prefix}{company.current_number:04d}/{year}"

    def assign_reference_if_needed(self):
        if not self.reference and self.status != 'DRAFT' and self.company:
            self.reference = self.generate_reference()
    
    def generate_payment_reference(self):
        if not self.reference:
            return ''
        clean_ref = self.reference.replace('/', '').replace('-', '')
        return f"{clean_ref[:8]}{self.client_name[:4].upper()}"
    
    def calculate_due_date(self):
        if not self.issue_date:
            return None
        
        import re
        terms_lower = self.payment_terms.lower()
        
        if 'on receipt' in terms_lower or 'due on receipt' in terms_lower:
            return self.issue_date
        
        days_match = re.search(r'(\d+)\s*days?', terms_lower)
        if days_match:
            from datetime import timedelta
            days = int(days_match.group(1))
            return self.issue_date + timedelta(days=days)
        
        if 'end of month' in terms_lower or 'eom' in terms_lower:
            from datetime import timedelta
            next_month = self.issue_date.replace(day=28) + timedelta(days=4)
            return next_month.replace(day=1) - timedelta(days=1)
        
        from datetime import timedelta
        return self.issue_date + timedelta(days=30)
    
    def calculate_retention_date(self):
        if not self.issue_date:
            return None
        return date(
            self.issue_date.year + RECORD_RETENTION_YEARS, 
            self.issue_date.month, 
            self.issue_date.day
        )
    
    def mark_as_paid(self, payment_date=None):
        self.status = 'PAID'
        self.payment_date = payment_date or date.today()
        self.save()
    
    def is_overdue(self):
        if self.status in ['PAID', 'CANCELLED', 'DRAFT']:
            return False
        if not self.due_date:
            return False
        return date.today() > self.due_date

    def get_tax_invoice_note(self):
        if not self.company.gst_registered:
            return "This is not a tax invoice. GST not applicable."
        
        if self.total_amount < TAX_INVOICE_THRESHOLD:
            return f"This invoice is not a tax invoice (total less than ${TAX_INVOICE_THRESHOLD} inc GST)."
        
        return ""

    def clean(self):
        super().clean()
        if self.client_type == 'BUSINESS' and not self.client_abn:
            raise ValidationError({
                'client_abn': 'ABN is required for business clients'
            })

    def save(self, *args, **kwargs):
        self.assign_reference_if_needed()
        
        if not self.payment_reference and self.reference:
            self.payment_reference = self.generate_payment_reference()
        
        if not self.due_date:
            self.due_date = self.calculate_due_date()
        
        if not self.retention_date:
            self.retention_date = self.calculate_retention_date()
        
        if self.status == 'SENT' and self.is_overdue():
            self.status = 'OVERDUE'
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference or 'DRAFT'} - {self.client_name}"

    class Meta:
        ordering = ['-issue_date', '-id']
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
        indexes = [
            models.Index(fields=['company', 'status'], name='invoicing_i_company_status_idx'),
            models.Index(fields=['issue_date', 'status'], name='invoicing_i_issue_status_idx'),
            models.Index(fields=['client_abn', 'status'], name='invoicing_i_abn_status_idx'),
            models.Index(fields=['-issue_date', '-id'], name='invoicing_i_issue_id_desc_idx'),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(
                    models.Q(client_type='INDIVIDUAL') | models.Q(client_abn__gt=''),
                ),
                name='client_abn_required_for_business'
            ),
            models.CheckConstraint(
                check=models.Q(due_date__gte=models.F('issue_date')),
                name='due_date_after_issue_date'
            ),
        ]


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(
        'Invoice',
        on_delete=models.CASCADE,
        related_name='items',
        db_index=True
    )
    description = models.TextField(verbose_name="Description")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantity")
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Unit price (ex GST)"
    )
    gst_treatment = models.CharField(
        max_length=20,
        choices=GST_TREATMENT,
        default='TAXABLE',
        verbose_name="GST treatment",
        help_text='How GST applies to this item'
    )
    
    @property
    def gst_rate(self):
        return GST_RATE if self.gst_treatment == 'TAXABLE' else GST_FREE_RATE
    
    @property
    def subtotal(self):
        return self.quantity * self.unit_price
    
    @property
    def gst_amount(self):
        if self.gst_treatment != 'TAXABLE':
            return Decimal('0.00')
        return self.subtotal * self.gst_rate / 100
    
    @property
    def total(self):
        return self.subtotal + self.gst_amount
    
    def __str__(self):
        return f"{self.description} - {self.quantity} x ${self.unit_price}"

    class Meta:
        verbose_name = "Invoice item"
        verbose_name_plural = "Invoice items"
        constraints = [
            models.CheckConstraint(
                check=models.Q(quantity__gt=0),
                name='quantity_positive'
            ),
            models.CheckConstraint(
                check=models.Q(unit_price__gt=0),
                name='unit_price_positive'
            ),
        ]
