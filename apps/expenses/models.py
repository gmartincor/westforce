from django.db import models
from django.utils.text import slugify
from apps.core.models import TimeStampedModel
import os


def expense_attachment_path(instance, filename):
    year = instance.date.year
    month = instance.date.month
    return f'expenses/{year}/{month:02d}/{filename}'


class ExpenseCategory(TimeStampedModel):
    
    class CategoryTypeChoices(models.TextChoices):
        FIXED = 'FIXED', 'Fixed'
        VARIABLE = 'VARIABLE', 'Variable'
        TAX = 'TAX', 'Tax'
        OCCASIONAL = 'OCCASIONAL', 'Occasional'
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Name"
    )
    
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name="Slug"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    
    category_type = models.CharField(
        max_length=20,
        choices=CategoryTypeChoices.choices,
        verbose_name="Category type"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
        db_index=True
    )

    class Meta:
        db_table = 'expense_categories'
        verbose_name = "Expense category"
        verbose_name_plural = "Expense categories"
        ordering = ['category_type', 'name']
        indexes = [
            models.Index(fields=['category_type', 'is_active']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"


class Expense(TimeStampedModel):
    
    class ServiceCategoryChoices(models.TextChoices):
        MOVING_OPERATIONS = 'moving_operations', 'Moving Operations'
        ADMINISTRATIVE = 'administrative', 'Administrative'
    
    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.PROTECT,
        related_name='expenses',
        verbose_name="Category"
    )
    
    service_category = models.CharField(
        max_length=20,
        choices=ServiceCategoryChoices.choices,
        default=ServiceCategoryChoices.MOVING_OPERATIONS,
        verbose_name="Service category"
    )
    
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Amount AUD"
    )
    
    date = models.DateField(
        verbose_name="Date"
    )
    
    description = models.TextField(
        verbose_name="Description"
    )
    
    accounting_year = models.PositiveIntegerField(
        verbose_name="Accounting year",
        db_index=True
    )
    
    accounting_month = models.PositiveSmallIntegerField(
        verbose_name="Accounting month",
        db_index=True
    )
    
    invoice_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Invoice number"
    )
    
    attachment = models.FileField(
        upload_to=expense_attachment_path,
        blank=True,
        null=True,
        verbose_name="Attachment"
    )

    class Meta:
        db_table = 'expenses'
        verbose_name = "Expense"
        verbose_name_plural = "Expenses"
        ordering = ['-date', '-created']
        indexes = [
            models.Index(fields=['accounting_year', 'accounting_month']),
            models.Index(fields=['category', 'date']),
            models.Index(fields=['date']),
            models.Index(fields=['accounting_year', 'category']),
            models.Index(fields=['service_category', 'date']),
        ]

    def save(self, *args, **kwargs):
        if self.date:
            self.accounting_year = self.date.year
            self.accounting_month = self.date.month
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category.name} - ${self.amount} AUD ({self.date})"

    def get_attachment_filename(self):
        if self.attachment:
            return os.path.basename(self.attachment.name)
        return None
