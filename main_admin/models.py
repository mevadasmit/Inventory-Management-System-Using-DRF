from django.db import models

from authentication.models import CustomUser
from base.models import BaseModel


# Create your models here.
class InventoryCategory(BaseModel):
    name = models.CharField(max_length=100,unique=True)

    def __str__(self):
        return self.name


class Organization(BaseModel):
    name = models.CharField(max_length=100,unique=True)
    email = models.EmailField(unique=True)
    address = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class InventoryManager(BaseModel):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization,on_delete=models.CASCADE)

    def __str__(self):
        return f"Org is : {self.organization.name} And IM is : {self.user.first_name}"