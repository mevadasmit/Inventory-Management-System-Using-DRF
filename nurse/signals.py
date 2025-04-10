from django.db.models.signals import post_save
from django.dispatch import receiver
from nurse.models import Request , RequestedItems
from django.core.exceptions import ValidationError
from django.utils.timezone import now

@receiver(post_save, sender=Request)
def handle_approval_and_stock_update(sender, instance, created, **kwargs):
    if not created and instance.status == "Approved":
        requested_items = instance.requested_items.all()
        for item in requested_items:
            org_inventory = item.inventory
            if org_inventory.quantity_in_stock < item.quantity_requested:
                raise ValidationError(
                    f"Insufficient stock for {org_inventory.inventory.name}"
                )
            org_inventory.quantity_in_stock -= item.quantity_requested
            org_inventory.save()


    if created and instance.is_emergency:
        instance.status = "Approved"
        instance.approved_by = instance.created_by
        instance.approved_at = now()
        instance.save()


@receiver(post_save, sender=RequestedItems)
def restore_stock_on_return(sender, instance, **kwargs):
    if instance.is_returned:
        inventory = instance.inventory
        inventory.quantity_in_stock += instance.quantity_requested
        inventory.save()