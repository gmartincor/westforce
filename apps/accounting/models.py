from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.core.models import TimeStampedModel


class ServiceTypeChoices(models.TextChoices):
    LOCAL_MOVE = 'local', 'Local Move'
    INTERSTATE_MOVE = 'interstate', 'Interstate Move'
    INTERNATIONAL_MOVE = 'international', 'International Move'
    STORAGE = 'storage', 'Storage Service'
    PACKING = 'packing', 'Packing Service'
    CLEANING = 'cleaning', 'Cleaning Service'
    OTHER = 'other', 'Other Service'


class PaymentMethodChoices(models.TextChoices):
    CARD = 'CARD', 'Credit/Debit Card'
    CASH = 'CASH', 'Cash'
    BANK_TRANSFER = 'BANK_TRANSFER', 'Bank Transfer'
    EFTPOS = 'EFTPOS', 'EFTPOS'
    PAYPAL = 'PAYPAL', 'PayPal'
    CHEQUE = 'CHEQUE', 'Cheque'
    OTHER = 'OTHER', 'Other'


class Income(TimeStampedModel):
    
    service_type = models.CharField(
        max_length=20,
        choices=ServiceTypeChoices.choices,
        default=ServiceTypeChoices.LOCAL_MOVE,
        verbose_name="Service type"
    )
    
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Amount"
    )
    
    date = models.DateField(
        default=timezone.now,
        verbose_name="Service date"
    )
    
    payment_method = models.CharField(
        max_length=15,
        choices=PaymentMethodChoices.choices,
        verbose_name="Payment method"
    )
    
    client_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Client name"
    )
    
    pickup_address = models.TextField(
        blank=True,
        verbose_name="Pickup address"
    )
    
    delivery_address = models.TextField(
        blank=True,
        verbose_name="Delivery address"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Service description"
    )
    
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Reference number"
    )
    
    accounting_year = models.PositiveIntegerField(
        verbose_name="Accounting year",
        db_index=True
    )
    
    accounting_month = models.PositiveSmallIntegerField(
        verbose_name="Accounting month",
        db_index=True
    )

    class Meta:
        db_table = 'incomes'
        verbose_name = "Income"
        verbose_name_plural = "Incomes"
        ordering = ['-date', '-created']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['accounting_year', 'accounting_month']),
            models.Index(fields=['service_type', 'date']),
        ]

    def clean(self):
        super().clean()
        
        if self.amount and self.amount <= 0:
            raise ValidationError({
                'amount': 'Amount must be greater than zero.'
            })

    def save(self, *args, **kwargs):
        if self.date:
            self.accounting_year = self.date.year
            self.accounting_month = self.date.month
        
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_service_type_display()} - ${self.amount} AUD ({self.date})"
