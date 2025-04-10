from django.urls import path
from supplier.views import ProductView, ProductDetailView, SupplierOrderListView

urlpatterns = [
    path('v1/supplier/inventory',ProductView.as_view(),name='products'),
    path('v1/supplier/inventory/details/<uuid:pk>',ProductDetailView.as_view(),name='products-details'),
    path('v1/supplier/order/all',SupplierOrderListView.as_view(),name='supplier-order'),

]