from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from main_admin.models import InventoryCategory, Organization, InventoryManager

# Register your models here.



class OrganizationResource(resources.ModelResource):
    class Meta:
        model = Organization


@admin.register(Organization)
class OrganizationAdmin(ImportExportModelAdmin):
    resource_class = OrganizationResource

admin.site.register(InventoryCategory)
admin.site.register(InventoryManager)