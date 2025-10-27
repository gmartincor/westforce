from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date
from apps.core.models import TimeStampedModel
from django.conf import settings


class Company(TimeStampedModel):
    LEGAL_FORMS = [
        ('SOLE_TRADER', 'Sole Trader'),
        ('PTY_LTD', 'Proprietary Limited Company (Pty Ltd)'),
        ('PUBLIC_COMPANY', 'Public Company Limited'),
        ('PARTNERSHIP', 'Partnership'),
        ('TRUST', 'Trust'),
        ('COOPERATIVE', 'Cooperative'),
    ]
    
    legal_form = models.CharField(max_length=20, choices=LEGAL_FORMS, verbose_name="Legal structure")
    business_name = models.CharField(max_length=200, verbose_name="Business name")
    legal_name = models.CharField(max_length=200, blank=True, verbose_name="Legal name")
    tax_id = models.CharField(max_length=15, verbose_name="ABN/ACN")
    address = models.TextField(verbose_name="Address")
    postal_code = models.CharField(max_length=10, verbose_name="Postcode")
    city = models.CharField(max_length=100, verbose_name="City/Suburb")
    province = models.CharField(max_length=100, blank=True, verbose_name="State")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Phone")
    email = models.EmailField(blank=True, verbose_name="Email")
    bank_name = models.CharField(max_length=100, verbose_name="Bank")
    iban = models.CharField(max_length=34, verbose_name="BSB/Account")
    mercantile_registry = models.CharField(max_length=200, blank=True, verbose_name="ASIC registration")
    share_capital = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Share capital")
    invoice_prefix = models.CharField(max_length=10, default="INV", verbose_name="Invoice prefix")
    current_number = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    logo = models.ImageField(upload_to='company/logos/', blank=True, null=True)

    def get_full_address(self):
        return f"{self.address}, {self.postal_code} {self.city}"

    def get_display_name(self):
        return self.legal_name or self.business_name

    def save(self, *args, **kwargs):
        if not self.pk and Company.objects.exists():
            raise ValidationError('Only one company can exist in the system.')
        super().save(*args, **kwargs)

    @property
    def is_freelancer(self):
        return self.legal_form == 'SOLE_TRADER'
    
    @property 
    def is_company(self):
        return self.legal_form != 'SOLE_TRADER'

    def __str__(self):
        return self.business_name

    class Meta:
        verbose_name_plural = "Companies"


class Invoice(TimeStampedModel):
    CLIENT_TYPES = [
        ('COMPANY', 'Company'),
        ('SOLE_TRADER', 'Sole Trader'),
        ('INDIVIDUAL', 'Individual'),
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent'),
        ('PAID', 'Paid'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    reference = models.CharField(max_length=50, unique=True, null=True, blank=True)
    issue_date = models.DateField(default=date.today, verbose_name="Issue date")
    client_type = models.CharField(max_length=20, choices=CLIENT_TYPES, verbose_name="Client type")
    client_name = models.CharField(max_length=200, verbose_name="Client name")
    client_tax_id = models.CharField(max_length=15, blank=True, verbose_name="Client ABN/ACN")
    client_address = models.TextField(verbose_name="Client address")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT', verbose_name="Status")
    payment_terms = models.TextField(default="Bank transfer", verbose_name="Payment terms")
    pdf_file = models.FileField(upload_to='invoices/pdfs/', blank=True)

    @property
    def base_amount(self):
        return sum(item.line_total for item in self.items.all())

    @property
    def gst_amount(self):
        return sum(item.gst_amount for item in self.items.all())

    @property
    def withholding_amount(self):
        return sum(item.withholding_amount for item in self.items.all())

    @property
    def total_amount(self):
        return self.base_amount + self.gst_amount - self.withholding_amount

    def generate_reference(self):
        if not self.issue_date:
            self.issue_date = date.today()
        year = self.issue_date.year % 100
        
        from django.db import transaction
        with transaction.atomic():
            company = Company.objects.select_for_update().get(pk=self.company.pk)
            company.current_number += 1
            company.save()
            return f"{company.invoice_prefix}{company.current_number:03d}_{year}"

    def assign_reference_if_needed(self):
        if not self.reference and self.status != 'DRAFT' and self.company:
            self.reference = self.generate_reference()

    def get_legal_note(self):
        if any(item.gst_rate == 0 for item in self.items.all()):
            return "GST exempt according to relevant GST legislation."
        return ""

    def save(self, *args, **kwargs):
        self.assign_reference_if_needed()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference or 'DRAFT'} - {self.client_name}"

    class Meta:
        ordering = ['-issue_date']


class InvoiceItem(models.Model):
    invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE, related_name='items')
    description = models.TextField(verbose_name="Description")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantity")
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Unit price"
    )
    gst_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('10.00'),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="GST (%)"
    )
    withholding_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('0.00'),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Withholding tax (%)"
    )
    
    @property
    def line_total(self):
        return self.quantity * self.unit_price
    
    @property
    def gst_amount(self):
        return self.line_total * self.gst_rate / 100
    
    @property
    def withholding_amount(self):
        return self.line_total * self.withholding_rate / 100
    
    def __str__(self):
        return f"{self.description} - {self.quantity} x ${self.unit_price} AUD"
