from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.utils import timezone

from base.pagination import MyLimitOffsetPagination
from base.role_access import RoleBasedPermission
from nurse.models import RequestedItems , Request
from nurse.serializers import RequestSerializer, ReturnableItemSerializer , ReturnInventorySerializer


# Create your views here.

class RequestedListView(generics.ListAPIView):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,RoleBasedPermission]
    allowed_roles = ['Inventory Manager','Nurse']
    pagination_class = MyLimitOffsetPagination

class RequestActionView(generics.UpdateAPIView):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,RoleBasedPermission]
    allowed_roles = ['Inventory Manager','Nurse']

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.status != 'Pending':
            raise ValidationError({"Details":"Request Already Processed."})

        action = request.data.get("action")

        if action == 'Approved':
            instance.status = 'Approved'
            instance.approved_by = request.user
            instance.approved_at = timezone.now()

        elif action == 'Rejected':
            instance.status = 'Rejected'
            instance.rejected_by = request.user
            instance.rejected_at = timezone.now()

        else:
            raise ValidationError({"Details":"Invalid Action."})

        instance.updated_by = request.user
        instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data,status=status.HTTP_200_OK)

class CreateRequestView(generics.CreateAPIView):
    serializer_class = RequestSerializer
    permission_classes = [permissions.IsAuthenticated, RoleBasedPermission]
    allowed_roles = ['Nurse']

    def get_queryset(self):
        return Request.objects.filter(nurse=self.request.user.nurse)

class RequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,RoleBasedPermission]
    allowed_roles = ['Inventory Manager','Nurse']

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.status != 'Pending':
            raise ValidationError({"Details": "Cannot Update, Request Already Processed."})

        items_data = request.data.get("requested_items", [])

        for item_data in items_data:
            try:
                requested_item = RequestedItems.objects.get(id=item_data["id"], request=instance)
                requested_item.quantity_requested = item_data.get("quantity_requested",
                                                                  requested_item.quantity_requested)
                requested_item.updated_by = request.user
                requested_item.save()
            except RequestedItems.DoesNotExist:
                raise ValidationError({"Details": f"Item with id {item_data['id']} not found in this request."})

        instance.updated_by = request.user
        instance.save()
        instance.update_total()

        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != 'Pending':
            raise ValidationError({"Details":"Cannot Delete, Request Already Processed."})

        self.perform_destroy(instance)
        return Response({"detail": "Request deleted successfully."},status=status.HTTP_204_NO_CONTENT)

class ReturnableItemView(generics.ListAPIView):
    serializer_class = ReturnableItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,RoleBasedPermission]
    allowed_roles = ['Inventory Manager','Nurse']
    pagination_class = MyLimitOffsetPagination

    def get_queryset(self):
        request_id = self.kwargs.get("request_id")
        return RequestedItems.objects.filter(request_id=request_id,
                                             inventory__inventory__is_reusable=True,
                                             is_returned = False)

class ReturnInventoryView(generics.CreateAPIView):
    serializer_class = ReturnInventorySerializer
    permission_classes = [permissions.IsAuthenticated, RoleBasedPermission]
    allowed_roles = ['Inventory Manager']

class ReturnStatusView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,RoleBasedPermission]
    allowed_roles = ['Inventory Manager']

    def retrieve(self, request, *args, **kwargs):
        request_id = self.kwargs.get("request_id")
        items = RequestedItems.objects.filter(request_id=request_id,
                                              inventory__inventory__is_reusable=True,)
        total = sum(item.quantity_requested for item in items)
        returned = sum(item.quantity_returned for item in items)
        pending = total - returned

        return Response({
            "total_requested": total,
            "total_returned": returned,
            "total_pending": pending,
        })