from django.db import models
from authentication.models import CustomUser
from base.models import BaseModel
from inventory_manager.models import Nurse, OrgInventory
from main_admin.models import Organization


# Create your models here.

class Request(BaseModel):

    STATUS_CHOICES = [("Pending", "Pending"),("Approved", "Approved"),("Rejected", "Rejected")]
    nurse = models.ForeignKey(Nurse, on_delete=models.CASCADE,related_name="requests")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    is_emergency = models.BooleanField(default=False)
    total_items = models.IntegerField(default=0)
    approved_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,null=True, blank=True, related_name="request_approved_by")
    rejected_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True,related_name="request_rejected_by")
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    status= models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending")


    def save(self, *args, **kwargs):
        if self.approved_by and self.rejected_by:
            raise ValueError("Request can't be both approved and rejected.")
        super().save(*args, **kwargs)

    def update_total(self):
        total = self.requested_items.values('inventory').distinct().count()
        self.total_items = total
        self.save()

    def __str__(self):
        return f"{self.nurse.user.first_name} - {self.status}"

class RequestedItems(BaseModel):
    request = models.ForeignKey(Request, on_delete=models.CASCADE,related_name="requested_items")
    inventory = models.ForeignKey(OrgInventory, on_delete=models.CASCADE)
    quantity_requested = models.IntegerField(default=1)
    quantity_returned = models.IntegerField(default=0)
    is_returned = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.inventory.inventory.name} - {self.quantity_requested}"