from rest_framework import serializers
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from inventory_manager.models import Nurse
from nurse.models import Request , RequestedItems

class RequestedItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = RequestedItems
        fields = ['id','inventory','quantity_requested','is_returned']
        extra_kwargs = {"id": {"read_only": True}}

class RequestSerializer(serializers.ModelSerializer):
    requested_items = RequestedItemSerializer(many=True)
    class Meta:
        model = Request
        fields = ['id','nurse','organization','is_emergency','total_items','status','approved_by','rejected_by','approved_at',
                  'rejected_at','requested_items']
        read_only_fields = ['approved_by','rejected_by','approved_at','rejected_at','total_items','status','nurse','organization']


    def create(self, validated_data):
        items_data = validated_data.pop("requested_items")
        nurse = Nurse.objects.get(user=self.context['request'].user)
        organization = nurse.organization
        is_emergency = validated_data.get('is_emergency', False)

        request_obj = Request.objects.create(
            nurse=nurse,
            organization=organization,
            is_emergency=is_emergency,
            created_by=self.context['request'].user,
            updated_by=self.context['request'].user,
            status='Approved' if is_emergency else 'Pending',
            approved_by=self.context['request'].user if is_emergency else None,
            approved_at=timezone.now() if is_emergency else None
        )

        for item in items_data:
            org_inventory = item['inventory']
            if org_inventory.quantity_in_stock < item['quantity_requested']:
                raise ValidationError(
                    {
                        "Details": f"Insufficient stock for {org_inventory.inventory.name}. Requested: {item['quantity_requested']}, Available: {org_inventory.quantity_in_stock}"
                    }
                )

            RequestedItems.objects.create(
                request=request_obj,
                created_by=self.context['request'].user,
                updated_by=self.context['request'].user,
                **item
            )

        request_obj.update_total()
        return request_obj

class ReturnableItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestedItems
        fields = ['id','inventory','quantity_requested','is_returned']

class ReturnInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestedItems
        fields = ['id', 'request', 'inventory', 'is_returned','quantity_requested','quantity_returned']
        read_only_fields = ['id', 'is_returned','quantity_requested']

    def validate(self, data):
        request_obj = data.get('request')
        inventory_obj = data.get('inventory')
        return_qty = data.get('quantity_returned')

        if not request_obj:
            raise serializers.ValidationError({"request": "This field is required."})
        if not inventory_obj:
            raise serializers.ValidationError({"inventory": "This field is required."})
        if not return_qty:
            raise serializers.ValidationError({"quantity_returned": "This field is required."})

        try:
            item = RequestedItems.objects.get(
                request=request_obj,
                inventory=inventory_obj,
                inventory__inventory__is_reusable=True,
            )
        except RequestedItems.DoesNotExist:
            raise serializers.ValidationError({
                "inventory": "Item not found in request, not reusable, or already returned."
            })

        pending = item.quantity_requested - item.quantity_returned
        if return_qty>pending:
            raise serializers.ValidationError({
                "quantity_returned": f"Cannot return more than pending. Pending: {pending}"
            })

        data['requested_item'] = item
        return data

    def create(self, validated_data):
        item = validated_data['requested_item']
        return_qty = validated_data.get('quantity_returned')
        item.quantity_returned += return_qty
        if item.quantity_returned == item.quantity_requested:
            item.is_returned = True
        item.updated_by = self.context['request'].user
        item.save()
        return item
