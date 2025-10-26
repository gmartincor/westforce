from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        verbose_name="Email address"
    )
    
    first_name = models.CharField(
        max_length=150,
        verbose_name="First name"
    )
    
    last_name = models.CharField(
        max_length=150,
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
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active"
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta:
        db_table = 'users'
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_display_name(self):
        return self.full_name or self.username
