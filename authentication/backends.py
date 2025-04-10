from django.contrib.auth.backends import ModelBackend
from .models import CustomUser

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = CustomUser.objects.get(email=username)  # Ensure login works with email
            if user.check_password(password):  # Verify password
                return user
        except CustomUser.DoesNotExist:
            return None
