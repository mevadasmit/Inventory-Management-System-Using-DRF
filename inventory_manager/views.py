from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from base.constants import DETAILS_FETCHED
from base.pagination import MyLimitOffsetPagination
from base.role_access import RoleBasedPermission
from base.utils import CustomUser
from inventory_manager.constants import (AVAILABLE_NURSES, NURSE_UPDATED, NURSE_UPDATE_FAILED, NURSE_DELETED,
                                         AVAILABLE_INVENTORY, AVAILABLE_SUPPLIER, SUPPLIER_INVENTORY, YOUR_ORDERS)
from inventory_manager.models import Nurse, OrgInventory
from rest_framework import generics
from inventory_manager.serializers import NurseSerializer, NurseDetailsSerializer, OrgInventorySerializer, \
    AvailableSupplierSerializer,SupplierInventorySerializer
from main_admin.models import InventoryManager
from main_admin.utils import success_response, error_response, delete_response
from order_management.models import Order
from order_management.serializers import OrderSerializer
from supplier.models import Inventory


# Create your views here.

class NurseView(generics.ListCreateAPIView):
    serializer_class = NurseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, RoleBasedPermission]
    allowed_roles = ['Inventory Manager']
    pagination_class = MyLimitOffsetPagination

    def get_queryset(self):
        user = self.request.user
        inventory_manager = InventoryManager.objects.filter(user=user).first()
        return Nurse.objects.filter(organization=inventory_manager.organization) if inventory_manager else Nurse.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page if page is not None else queryset, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return success_response(AVAILABLE_NURSES, serializer.data, status.HTTP_200_OK)

class NurseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NurseDetailsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, RoleBasedPermission]
    allowed_roles = ['Inventory Manager']

    def get_object(self):
        return get_object_or_404(Nurse, pk=self.kwargs.get('pk')).user

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return success_response(DETAILS_FETCHED, serializer.data, status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return success_response(NURSE_UPDATED, serializer.data, status.HTTP_200_OK)
        return error_response(serializer.errors, NURSE_UPDATE_FAILED, status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return delete_response(NURSE_DELETED, status.HTTP_204_NO_CONTENT)

class OrgInventoryView(generics.ListAPIView):
    serializer_class = OrgInventorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, RoleBasedPermission]
    allowed_roles = ['Inventory Manager']
    pagination_class = MyLimitOffsetPagination
    pagination_message = AVAILABLE_INVENTORY

    def get_queryset(self):
        user = self.request.user
        try:
            inventory_manager = InventoryManager.objects.get(user=user)
            return OrgInventory.objects.filter(organization=inventory_manager.organization)
        except InventoryManager.DoesNotExist:
            return OrgInventory.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page if page is not None else queryset, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return success_response(serializer.data, status.HTTP_200_OK)

class AvailableSupplierView(generics.ListAPIView):
    serializer_class = AvailableSupplierSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, RoleBasedPermission]
    allowed_roles = ['Inventory Manager']
    pagination_class = MyLimitOffsetPagination
    pagination_message = AVAILABLE_SUPPLIER

    def get_queryset(self):
        return CustomUser.objects.filter(role="Supplier")

class SupplierInventoryView(generics.ListAPIView):
    serializer_class = SupplierInventorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, RoleBasedPermission]
    allowed_roles = ['Inventory Manager']
    pagination_class = MyLimitOffsetPagination
    pagination_message = SUPPLIER_INVENTORY

    def get_queryset(self):
        supplier_id = self.kwargs.get('pk')
        return Inventory.objects.filter(supplier_id = supplier_id)

class IMOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, RoleBasedPermission)
    allowed_roles = ['Inventory Manager']
    pagination_class = MyLimitOffsetPagination
    pagination_message = YOUR_ORDERS

    def get_queryset(self):
        user = self.request.user
        try:
            inventory_manager = InventoryManager.objects.get(user=user)
        except InventoryManager.DoesNotExist:
            return Order.objects.none()
        return Order.objects.filter(inventory_manager=inventory_manager).order_by("-created")