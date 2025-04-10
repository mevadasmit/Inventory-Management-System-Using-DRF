from django.urls import path
from inventory_manager.views import NurseView, NurseDetailView, OrgInventoryView, AvailableSupplierView, \
    SupplierInventoryView, IMOrderListView

urlpatterns = [
    path('v1/inventory/manager/nurse',NurseView.as_view(),name='nurse'),
    path('v1/inventory/manager/nurse/details/<uuid:pk>',NurseDetailView().as_view(),name='user'),
    path('v1/inventory/manager/org/inventory',OrgInventoryView.as_view(),name='org-inventory'),
    path('v1/inventory/manager/supplier/all',AvailableSupplierView.as_view(),name='supplier-all'),
    path('v1/inventory/manager/supplier/all/<uuid:pk>',SupplierInventoryView.as_view(),name='supplier-inventory'),
    path('v1/inventory/manager/order/all',IMOrderListView.as_view(),name='Inventory-Manager-Order')
]