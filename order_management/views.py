from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from base.pagination import MyLimitOffsetPagination
from base.role_access import RoleBasedPermission
from order_management.serializers import CartSerializer, OrderSerializer
from order_management.models import Cart, CartItem , Order , OrderItem
from main_admin.models import InventoryManager
from rest_framework.exceptions import NotFound
from supplier.models import Inventory


# Create your views here.

class CartDetailView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, RoleBasedPermission)
    allowed_roles = ['Inventory Manager']

    def get_object(self):
        try:
            inventory_manager = InventoryManager.objects.get(user=self.request.user)
        except InventoryManager.DoesNotExist:
            raise NotFound("Inventory Manager not found for the current user.")

        cart, _ = Cart.objects.get_or_create(inventory_manager=inventory_manager)
        return cart

class AddToCartView(generics.CreateAPIView):
    serializer_class = CartSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, RoleBasedPermission)
    allowed_roles = ['Inventory Manager']

    def create(self, request, *args, **kwargs):
        user = request.user
        inventory_id = request.data.get('inventory_id')
        quantity = int(request.data.get('quantity',1))

        inventory_manager = InventoryManager.objects.get(user=self.request.user)

        cart,_ = Cart.objects.get_or_create(inventory_manager=inventory_manager,
                                            defaults={"created_by":user , "updated_by":user})

        try:
            inventory = Inventory.objects.get(id=inventory_id)
        except Inventory.DoesNotExist:
            return Response({"Error":"Inventory ID not found for the current user."}, status=status.HTTP_404_NOT_FOUND)

        if quantity > inventory.quantity:
            return Response(
                {"Error":"Not Enough items available in supplier's inventory."},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item , created = CartItem.objects.get_or_create(
            cart = cart, inventory = inventory ,
            defaults={'quantity' : quantity,"supplier":inventory.supplier,
                        "created_by":user,"updated_by":user})

        if not created:
            if cart_item.quantity + quantity > inventory.quantity:
                return Response(
                    {"Error":"Total quantity exceeds available stock."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart_item.quantity += int(quantity)
            cart_item.updated_by = user
            cart_item.save()

        cart.updated_by = user
        cart.save()
        return Response(({"message":"Item added to cart."},request.data),status=status.HTTP_201_CREATED)

class UpdateToCartView(generics.UpdateAPIView,generics.DestroyAPIView):
    serializer_class = CartSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, RoleBasedPermission)
    allowed_roles = ['Inventory Manager']

    def get_object(self):
        return get_object_or_404(CartItem, pk=self.kwargs['pk'])

    def update(self, request, *args, **kwargs):
        user = request.user
        cart_item = self.get_object()
        new_quantity = int(request.data.get('quantity',1))
        inventory = cart_item.inventory

        if new_quantity > inventory.quantity:
            return Response(
                {"Error":"Requested quantity exceeds in available supplier's inventory.",
                 "Available Quantity":inventory.quantity},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item.quantity = new_quantity
        cart_item.updated_by = user
        cart_item.save()

        cart_item.cart.updated_by = user
        cart_item.cart.save()

        return Response({"message":"Cart Item updated."},status=status.HTTP_200_OK)


    def destroy(self, request, *args, **kwargs):
        user = request.user
        cart_item = self.get_object()

        cart = cart_item.cart
        cart_item.delete()

        cart.updated_by = user
        cart.save()

        return Response({"message":"Cart Item Removed."},status=status.HTTP_204_NO_CONTENT)

class OrderCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, RoleBasedPermission)
    allowed_roles = ['Inventory Manager']
    pagination_class = MyLimitOffsetPagination

    def create(self, request, *args, **kwargs):
        user = request.user
        inventory_manager = InventoryManager.objects.get(user=user)

        cart,_ = Cart.objects.get_or_create(inventory_manager=inventory_manager)

        if not cart.cart_items.exists():
            return Response({"Error":"Cart is Empty , Items does not exist."},status=status.HTTP_400_BAD_REQUEST)

        supplier = cart.cart_items.first().inventory.supplier

        order = Order.objects.create(
            supplier = supplier,
            inventory_manager = inventory_manager,
            total_price=cart.total_price,
            total_products=cart.total_products,
            created_by=user,
            updated_by=user,
        )

        for item in cart.cart_items.all():
            OrderItem.objects.create(
                order=order,
                inventory=item.inventory,
                quantity=item.quantity,
                unit_price=item.inventory.unit_price,
                total_price=item.total_price,
                created_by=user,
                updated_by=user,
            )


        cart.cart_items.all().delete()
        cart.total_price = 0
        cart.total_products = 0
        cart.updated_by = user
        cart.save()

        return Response(OrderSerializer(order).data,status=status.HTTP_201_CREATED)

class OrderUpdateView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, RoleBasedPermission)
    allowed_roles = ['Inventory Manager','Supplier']

    def update(self, request, *args, **kwargs):
        user = request.user
        order = self.get_object()
        new_status = request.data.get('status',None)

        if new_status not in ["Delivered","Confirmed"]:
            return Response({"Error":"Invalid status Update."},status=status.HTTP_400_BAD_REQUEST)

        if new_status == "Delivered":
            if user.role != "Supplier" or user != order.supplier:
                return Response({"Error":"Only supplier can update status to delivered"},status=status.HTTP_403_FORBIDDEN)

            if order.status != "Pending":
                return Response({"Error":"Only pending order can update status as delivered"},status=status.HTTP_400_BAD_REQUEST)

            order.status = "Delivered"
            order.delivered_by = user
            order.delivered_at = timezone.now()

        elif new_status == "Confirmed":
            if user.role != "Inventory Manager" or order.inventory_manager.user != user:
                return Response({"error": "Only the assigned inventory manager can confirm this order"},
                                status=status.HTTP_403_FORBIDDEN)

            if order.status != "Delivered":
                return Response({"error": "Only delivered orders can be confirmed"}, status=status.HTTP_400_BAD_REQUEST)

            order.status = "Confirmed"
            order.confirmed_by = user
            order.confirmed_at = timezone.now()

        order.updated_by = user
        order.updated_at = timezone.now()
        order.save()

        return Response({"message": f"Order status updated to {new_status}"},status=status.HTTP_200_OK)