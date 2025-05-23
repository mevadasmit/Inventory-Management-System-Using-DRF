# inventory/tasks.py

from celery import shared_task
from django.core.mail import send_mail
from .models import Order

@shared_task
def send_order_confirmed_email(order_id):
    try:
        order = Order.objects.select_related('confirmed_by', 'supplier__user').get(pk=order_id)
        subject = f"Order #{order.id} Confirmed"
        message = (
            f"Hello {order.supplier.user.first_name()},\n\n"
            f"Your order #{order.id} was confirmed by "
            f"{order.confirmed_by.first_name()}.\n\n"
            "Thank you."
        )
        send_mail(subject, message, "no-reply@hospital.com",
                  [order.supplier.user.email])
    except Order.DoesNotExist:
        pass
