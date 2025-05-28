from django.apps import AppConfig

class AdminConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "main_admin"

    def ready(self):
        import main_admin.signals  # Import only, don't access DB here
