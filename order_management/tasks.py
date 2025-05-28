from celery import shared_task
from django.core.mail import send_mail
from .models import Order
from hospital_inventory_management import settings
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_order_confirmed_email(self, order_id):
    try:
        order = Order.objects.select_related('confirmed_by', 'supplier').get(pk=order_id)

        subject = f"Order #{order.id} Confirmed"
        message = (
            f"Hello {order.supplier.first_name},\n\n"
            f"Your order #{order.id} was confirmed by "
            f"{order.confirmed_by.first_name}.\n\n"
            "Thank you."
        )
        send_mail(subject, message, settings.EMAIL_HOST_USER, [order.supplier.email])
    except Order.DoesNotExist:
        logger.warning(f"Order with ID {order_id} not found.")
    except Exception as exc:
        logger.error(f"Email sending failed for order {order_id}: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_order_delivered_email_to_manager(self, order_id):
    try:
        order = Order.objects.select_related('supplier', 'inventory_manager__user', 'delivered_by').get(pk=order_id)

        manager_email = order.inventory_manager.user.email
        manager_name = order.inventory_manager.user.first_name
        supplier_name = order.supplier.first_name

        subject = f"Order #{order.id} Delivered by {supplier_name}"
        message = (
            f"Hello {manager_name},\n\n"
            f"The order #{order.id} has been marked as *Delivered* by {supplier_name}.\n"
            f"Please login to the system and confirm the delivery from your side to update the stock.\n\n"
            f"Thanks,\n"
            f"Inventory System"
        )

        send_mail(subject, message, settings.EMAIL_HOST_USER, [manager_email])
    except Order.DoesNotExist:
        logger.warning(f"Order with ID {order_id} not found.")
    except Exception as exc:
        logger.error(f"Email sending failed for delivery confirmation to manager (Order {order_id}): {exc}")
        raise self.retry(exc=exc, countdown=60)
