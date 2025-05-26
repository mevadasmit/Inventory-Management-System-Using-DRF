from django.apps import AppConfig

class AdminConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "main_admin"

    def ready(self):
        try:
            from main_admin.tasks import export_org_csv
            from django_celery_beat.models import PeriodicTask , IntervalSchedule
            from django.db.utils import OperationalError , ProgrammingError

            schedule, _ = IntervalSchedule.objects.get_or_create(
                every=2,
                period=IntervalSchedule.MINUTES,
            )

            periodic_task = PeriodicTask.objects.get_or_create(
                interval=schedule,
                name="Export Org CSV Every 2 Minutes",
                task="main_admin.tasks.export_org_csv",
            )
        except (OperationalError, ProgrammingError) as e:
            pass
