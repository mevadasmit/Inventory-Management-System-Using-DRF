from django.db import models
from authentication.models import CustomUser
from base.models import BaseModel
from main_admin.models import InventoryManager, Organization
from supplier.models import Inventory

# Create your models here.

class Nurse(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    inventory_manager = models.ForeignKey(InventoryManager, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __str__(self):
        return f" {self.organization.name} {self.user.first_name} {self.user.last_name}"


class OrgInventory(BaseModel):
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    quantity_in_stock = models.IntegerField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __str__(self):
        return f"Inventory Name : {self.inventory.name}"