from django.urls import path

from order_management.views import CartDetailView, AddToCartView, UpdateToCartView , OrderUpdateView , OrderCreateView

urlpatterns = [
    path('v1/cart',CartDetailView.as_view(),name='cart-detail'),
    path('v1/cart/inventory/',AddToCartView.as_view(),name='cart-inventory'),
    path('v1/cart/inventory/<uuid:pk>',UpdateToCartView.as_view(),name='cart-update-delete'),
    path('v1/order',OrderCreateView.as_view(),name='order-create'),
    path('v1/order/update-status/<uuid:pk>',OrderUpdateView.as_view(),name='order-update-status'),

]