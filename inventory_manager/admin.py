from django.contrib import admin

from inventory_manager.models import Nurse, OrgInventory

# Register your models here.

admin.site.register(Nurse)
admin.site.register(OrgInventory)