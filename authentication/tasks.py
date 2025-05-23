from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from hospital_inventory_management import settings

User = get_user_model()

@shared_task
def send_password_changed_email(user_id):
    try:
        user = User.objects.get(pk=user_id)
        subject = "Your Hospital Inventory password was changed"
        message = (
            f"Hello {user.first_name or user.email},\n\n"
            "This is a confirmation that the password for your account "
            "was just changed. If you did not perform this action, please "
            "contact support immediately.\n\n"
            "— The Hospital Inventory Team"
        )

        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email]
                  ,fail_silently=False,)

    except User.DoesNotExist:
        raise Exception("User not found")