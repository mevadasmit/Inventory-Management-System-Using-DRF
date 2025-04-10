from rest_framework.response import Response
from rest_framework import serializers
from order_management.models import Cart,CartItem,Order,OrderItem


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id','inventory','quantity','total_price']

class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True,read_only=True)
    class Meta:
        model = Cart
        fields = ['id','inventory_manager','total_products','total_price','cart_items']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id','inventory','quantity','unit_price','total_price']

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True,read_only=True)
    class Meta:
        model = Order
        fields = ['id','inventory_manager','total_products','total_price','status','order_items','delivered_by','confirmed_by']
        extra_kwargs = {'id': {'read_only': True},
                        'delivered_by': {'read_only': True},
                        'confirmed_by': {'read_only': True},}