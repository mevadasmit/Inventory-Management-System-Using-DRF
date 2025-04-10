from django.db import models

from authentication.models import CustomUser
from base.models import BaseModel
from main_admin.models import InventoryCategory

# Create your models here.

class Inventory(BaseModel):
    name = models.CharField(max_length=100)
    supplier = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    category = models.ForeignKey(InventoryCategory,on_delete=models.CASCADE)
    unit_price = models.IntegerField(default=0)
    quantity = models.IntegerField(default=0)
    is_reusable = models.BooleanField(default=False)

    def __str__(self):
        return f"Product Name: {self.name}"