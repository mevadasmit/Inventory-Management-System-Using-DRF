from rest_framework import generics, permissions, status
from rest_framework.response import Response
from base.pagination import MyLimitOffsetPagination
from base.role_access import RoleBasedPermission
from order_management.serializers import OrderSerializer
from supplier.models import Inventory
from supplier.serializers import InventorySerializer, InventoryDetailsSerializer
from order_management.models import Order


# Create your views here.
class ProductView(generics.ListCreateAPIView):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, RoleBasedPermission)
    allowed_roles = ['Supplier']
    pagination_class = MyLimitOffsetPagination

    def perform_create(self, serializer):
        supplier = self.request.user
        serializer.save(supplier= supplier, created_by=supplier, updated_by=supplier)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(({'Product Added Successfully:'}, serializer.data), status=status.HTTP_201_CREATED,
                        headers=headers)

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Inventory.objects.all()
    serializer_class = InventoryDetailsSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, RoleBasedPermission)
    allowed_roles = ['Supplier']

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(({'Product Details Are:'}, serializer.data), status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.supplier != request.user:
            return Response({'error': 'You are not authorized to update this product.'},
                            status=status.HTTP_403_FORBIDDEN)
        if 'supplier' in request.data and request.data['supplier'] != str(instance.supplier.id):
            return Response({'error': 'Supplier cannot be changed.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user, supplier=instance.supplier)

        return Response({'message': 'Product updated successfully', 'data': serializer.data}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.supplier != request.user:
            return Response({'error': 'You are not authorized to delete this product.'},
                            status=status.HTTP_403_FORBIDDEN)
        instance.delete()
        return Response({'message': 'Product deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

class SupplierOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, RoleBasedPermission)
    allowed_roles = ['Supplier']
    pagination_class = MyLimitOffsetPagination

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(supplier=user).order_by("-created")