from django.contrib import admin
from main_admin.models import InventoryCategory, Organization, InventoryManager

# Register your models here.

admin.site.register(InventoryCategory)
admin.site.register(Organization)
admin.site.register(InventoryManager)