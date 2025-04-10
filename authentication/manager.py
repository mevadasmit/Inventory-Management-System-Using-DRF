from django.contrib.auth.models import BaseUserManager
from authentication.constants import (SUPERUSER_EMAIL_VALIDATION_ERROR)

class CustomUserManager(BaseUserManager):
    """
        Custom user manager for managing user creation and superuser creation.

        This manager uses email as the username and handles setting the password
        and required fields for superusers.
    """

    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(SUPERUSER_EMAIL_VALIDATION_ERROR)

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, password, **extra_fields)
