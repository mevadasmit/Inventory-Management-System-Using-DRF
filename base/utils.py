from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator

CustomUser = get_user_model()
token_generator = PasswordResetTokenGenerator()
def send_registration_email(user, raw_password):
    """
    Sends a registration email with login credentials.

    :param user: CustomUser instance (Registered User)
    :param raw_password: Generated password for the user
    """
    subject = "Welcome to Medivault - Registration Successful"
    message = f"""
    Hello {user.first_name},

    Your registration was successful! You can log in with the following credentials:

    🔹 **Login Email:** {user.email}  
    🔹 **Login Password:** {raw_password}  

    You must log in first and reset your password.

    ➡️ [Click here to log in](http://localhost:8000/api/v1/user/login)

    Please keep your credentials secure.

    Regards,  
    **Medivault Team**
    """
    try:
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
    except Exception as e:
        raise RuntimeError(f"Failed to send email to {user.email}") from e

def send_password_reset_email(user, request=None):
    if not isinstance(user, CustomUser):
        raise ValueError("User must be an instance of CustomUser")

    token = token_generator.make_token(user)
    reset_link = f"localhost:8000/api/v1/user/reset-password/?token={token}"

    subject = "Password Reset Request"
    message = f"""
    Hi {user.first_name or 'User'},

    You requested a password reset. Click the link below to reset your password:
    {reset_link}

    Regards,
    Your Team
    """
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False,)
    except Exception as e:
        raise f"Failed to send email to {user.email} " from e
    return token