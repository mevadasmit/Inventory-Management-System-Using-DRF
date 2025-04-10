"""
URL configuration for hospital_inventory_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path , include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path("api/", include("authentication.urls")),
    path("api/", include("main_admin.urls")),
    path("api/",include("inventory_manager.urls")),
    path("api/",include("supplier.urls")),
    path("api/",include("order_management.urls")),
    path("api/",include("nurse.urls")),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
