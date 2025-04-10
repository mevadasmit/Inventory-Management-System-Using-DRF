from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from authentication.manager import CustomUserManager
from base.models import BaseModel
from PIL import Image
from base.constants import (FIELD_SUPPLIER,FIELD_NURSE,FIELD_IM,FIELD_ADMIN)
from authentication.constants import (DEFAULT_BIO)


class CustomUser(AbstractBaseUser,BaseModel,PermissionsMixin):
    """
        Custom user model.

        This model represents a user in the system, using email as the username
        and providing additional fields like role and first-time login status.
    """
    ROLE_CHOICES = [(FIELD_ADMIN,FIELD_ADMIN),(FIELD_IM,FIELD_IM),(FIELD_NURSE,FIELD_NURSE),(FIELD_SUPPLIER,FIELD_SUPPLIER)]

    username = None
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=30 , unique=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    is_first_time_login = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)


    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name','phone_number']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Profile(BaseModel):
    """
        Represents a user's profile.

        This model extends the BaseModel and stores additional information about a user,
        including their profile image and a short bio. The profile image is automatically
        resized upon saving.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE ,related_name='profile')
    image = models.ImageField(upload_to='profile_pics/',blank=True,null=True,default='profile_pics/default.jpg')
    bio = models.TextField(blank=True,null=True,default=DEFAULT_BIO)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}'s Profile"

    def save(self, *args, **kwargs):
        """Resize profile image to max 300x300 on save."""
        super().save(*args, **kwargs)

        if self.image:  # Ensure an image is uploaded
            img = Image.open(self.image.path)
            if img.height > 300 or img.width > 300:
                img.thumbnail((300, 300))
                img.save(self.image.path)
