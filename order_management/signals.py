from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from inventory_manager.models import OrgInventory
from order_management.models import Order
from order_management.tasks import send_order_confirmed_email, send_order_delivered_email_to_manager


@receiver(post_save, sender=Order)
def update_stock_on_confirm(sender, instance, created, **kwargs):
    if not created and instance.status == "Confirmed":
        for item in instance.order_items.all():
            inventory = item.inventory

            inventory.quantity -= item.quantity
            inventory.save()

            org_inventory, _ = OrgInventory.objects.get_or_create(
                inventory=inventory,
                organization=instance.inventory_manager.organization,
                created_by=instance.created_by,
                updated_by=instance.updated_by,
                defaults={'quantity_in_stock': 0}
            )
            org_inventory.quantity_in_stock += item.quantity
            org_inventory.save()

        transaction.on_commit(
            lambda: send_order_confirmed_email.delay(order_id=instance.id, )
        )
    elif instance.status == "Delivered":
        transaction.on_commit(
            lambda: send_order_delivered_email_to_manager.delay(order_id=instance.id)
        )
