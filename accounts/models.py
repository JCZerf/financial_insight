from __future__ import annotations

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import EmailValidator
from django.db import models
from django.utils import timezone

from accounts.managers import UserManager
from accounts.validators import normalize_cpf, normalize_name, validate_birth_date, validate_cpf, validate_full_name


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        unique=True,
        max_length=254,
        validators=[EmailValidator(message="Enter a valid email address.")],
    )
    name = models.CharField(max_length=255, validators=[validate_full_name])
    birth_date = models.DateField(validators=[validate_birth_date])
    cpf = models.CharField(max_length=11, unique=True, validators=[validate_cpf])
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_authorized = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "birth_date", "cpf"]

    class Meta:
        db_table = "account_user"
        indexes = [
            models.Index(fields=["email"], name="idx_account_user_email"),
            models.Index(fields=["cpf"], name="idx_account_user_cpf"),
            models.Index(fields=["is_active", "is_authorized"], name="idx_account_user_status"),
        ]

    def save(self, *args, **kwargs):
        self.email = (self.email or "").strip().lower()
        self.name = normalize_name(self.name)
        self.cpf = normalize_cpf(self.cpf)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.email
