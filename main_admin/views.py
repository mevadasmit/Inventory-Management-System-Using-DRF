from rest_framework import generics , status
from authentication.models import CustomUser
from base.constants import DETAILS_FETCHED, FIELD_ADMIN
from base.pagination import MyLimitOffsetPagination
from base.role_access import RoleBasedPermission
from rest_framework import permissions
from main_admin.constants import (AVAILABLE_USERS, USER_UPDATED_SUCCESS, USER_DELETED_SUCCESS, USER_UPDATED_FAILURE,
                                  AVAILABLE_INVENTORY, CATEGORY_CREATED, CATEGORY_CREATION_FAILED,
                                  CATEGORY_DETAIL_FETCHED, CATEGORY_UPDATED, INVENTORY_UPDATE_FAILED, CATEGORY_DELETED,
                                  AVAILABLE_ORGANIZATION, ORGANIZATION_CREATED, ORGANIZATION_UPDATED,
                                  ORGANIZATION_DELETED, ORGANIZATION_CREATION_FAILED, ORGANIZATION_UPDATE_FAILED)
from main_admin.models import InventoryCategory, Organization
from main_admin.serializers import UserListSerializer, InventoryCategorySerializer, OrganizationSerializer, \
    OrganizationDetailSerializer
from main_admin.utils import delete_response, success_response, error_response
from supplier.models import Inventory


# Create your views here

class UserListViewAPI(generics.ListAPIView):
    serializer_class = UserListSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, RoleBasedPermission]
    allowed_roles = [FIELD_ADMIN]
    pagination_class = MyLimitOffsetPagination
    pagination_message = AVAILABLE_USERS

class UserDetailViewAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,RoleBasedPermission]
    allowed_roles = [FIELD_ADMIN]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=self.request.user)
            return success_response(USER_UPDATED_SUCCESS, serializer.data, status.HTTP_200_OK)
        return error_response(serializer.errors, USER_UPDATED_FAILURE , status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return delete_response(USER_DELETED_SUCCESS, status.HTTP_204_NO_CONTENT)

class InventoryView(generics.ListCreateAPIView):
    queryset = Inventory.objects.all()
    serializer_class = InventoryCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,RoleBasedPermission]
    allowed_roles = [FIELD_ADMIN]
    pagination_class = MyLimitOffsetPagination
    pagination_message = AVAILABLE_INVENTORY

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=self.request.user,updated_by=self.request.user)
            return success_response(CATEGORY_CREATED, serializer.data, status.HTTP_201_CREATED)
        return error_response(serializer.errors, CATEGORY_CREATION_FAILED, status.HTTP_400_BAD_REQUEST)

class InventoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = InventoryCategory.objects.all()
    serializer_class = InventoryCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,RoleBasedPermission]
    allowed_roles = [FIELD_ADMIN]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(CATEGORY_DETAIL_FETCHED, serializer.data, status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=self.request.user)
            return success_response(CATEGORY_UPDATED, serializer.data, status.HTTP_200_OK)
        return error_response(serializer.errors, INVENTORY_UPDATE_FAILED, status.HTTP_400_BAD_REQUEST)

    def destroy(self, request,*args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return delete_response(CATEGORY_DELETED, status.HTTP_200_OK)

class OrganizationView(generics.ListCreateAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated, RoleBasedPermission]
    allowed_roles = [FIELD_ADMIN]
    pagination_class = MyLimitOffsetPagination
    pagination_message = AVAILABLE_ORGANIZATION

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            organization = serializer.save()
            data = self.get_serializer(organization).data
            return success_response(ORGANIZATION_CREATED, data, status.HTTP_201_CREATED)
        return error_response(serializer.errors,ORGANIZATION_CREATION_FAILED,status.HTTP_400_BAD_REQUEST)

class OrganizationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationDetailSerializer
    permission_classes = [permissions.IsAuthenticated, RoleBasedPermission]
    allowed_roles = [FIELD_ADMIN]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = OrganizationDetailSerializer(instance)
        return success_response(DETAILS_FETCHED, serializer.data, status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = OrganizationDetailSerializer(instance,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=self.request.user)
            return success_response(ORGANIZATION_UPDATED, serializer.data, status.HTTP_200_OK)
        return error_response(serializer.errors, ORGANIZATION_UPDATE_FAILED, status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return delete_response(ORGANIZATION_DELETED,status.HTTP_204_NO_CONTENT)