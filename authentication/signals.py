from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile, CustomUser

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a Profile when a new CustomUser is created."""
    if created:
        Profile.objects.create(user=instance)  # Create profile with default values

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """Ensure profile is saved when user is saved."""
    instance.profile.save()
