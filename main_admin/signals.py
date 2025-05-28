from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import logging

logger = logging.getLogger(__name__)

@receiver(post_migrate)
def setup_periodic_tasks(sender, **kwargs):
    try:
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=2,
            period=IntervalSchedule.HOURS,
        )
        logger.info(f"IntervalSchedule {'created' if created else 'exists'}: {schedule}")

        periodic_task, created = PeriodicTask.objects.update_or_create(
            interval=schedule,
            name="Export Org CSV Every 2 Hours",
            task="main_admin.tasks.export_org_csv",
        )
        logger.info(f"PeriodicTask {'created' if created else 'exists'}: {periodic_task}")
    except Exception as e:
        logger.warning(f"Could not set up periodic tasks: {e}")
