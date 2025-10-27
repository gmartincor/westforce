from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        verbose_name="Email address"
    )
    
    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="First name"
    )
    
    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Last name"
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Phone number"
    )
    
    position = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Position/Title"
    )
    
    company_name = models.CharField(
        max_length=200,
        default="Westforce Moving Company",
        verbose_name="Company name"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active"
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = 'users'
        verbose_name = "Manager User"
        verbose_name_plural = "Manager Users"

    def clean(self):
        super().clean()
        if not self.pk and User.objects.exists():
            raise ValidationError("Only one manager user is allowed in the system.")

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.full_clean()
        if not self.is_staff:
            self.is_staff = True
        if not self.is_superuser:
            self.is_superuser = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_display_name()} - {self.company_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_display_name(self):
        return self.full_name or self.username

    @classmethod
    def get_manager(cls):
        try:
            return cls.objects.filter(is_active=True).first()
        except cls.DoesNotExist:
            return None
