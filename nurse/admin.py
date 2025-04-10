from django.contrib import admin

from nurse.models import Request, RequestedItems

# Register your models here.

admin.site.register(Request)
admin.site.register(RequestedItems)