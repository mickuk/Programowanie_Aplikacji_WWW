from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import Group, Permission

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    # Dodaj related_name do pól groups i user_permissions
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',  # Unikalna nazwa dla odwrotnego dostępu
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',  # Unikalna nazwa dla odwrotnego dostępu
        blank=True
    )
