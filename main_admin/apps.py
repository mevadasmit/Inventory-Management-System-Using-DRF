from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class AdminConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "main_admin"

    def ready(self):
        try:
            from main_admin.tasks import export_org_csv
            from django_celery_beat.models import PeriodicTask, IntervalSchedule
            from django.db.utils import OperationalError, ProgrammingError

            schedule, created = IntervalSchedule.objects.get_or_create(
                every=10,
                period=IntervalSchedule.MINUTES,
            )
            logger.info(f"IntervalSchedule {'created' if created else 'exists'}: {schedule}")

            periodic_task, created = PeriodicTask.objects.get_or_create(
                interval=schedule,
                name="Export Org CSV Every 2 Minutes",
                task="main_admin.tasks.export_org_csv",
            )
            logger.info(f"PeriodicTask {'created' if created else 'exists'}: {periodic_task}")

        except (OperationalError, ProgrammingError) as e:
            logger.warning(f"Database not ready or error: {e}")
