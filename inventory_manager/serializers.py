from django.db import transaction
from django.utils.crypto import get_random_string
from rest_framework import serializers
from authentication.models import CustomUser
from base.utils import send_registration_email
from inventory_manager.models import Nurse, OrgInventory
from main_admin.models import InventoryManager
from main_admin.serializers import UserListSerializer
from supplier.models import Inventory

class NurseSerializer(serializers.ModelSerializer):
    nurse = UserListSerializer(write_only=True)

    class Meta:
        model = Nurse
        fields = ['id', 'nurse', 'inventory_manager', 'organization']

    def create(self, validated_data):
        nurse_data = validated_data.pop('nurse')
        request_user = self.context['request'].user

        inventory_manager = InventoryManager.objects.filter(user=request_user).first()
        if not inventory_manager:
            raise serializers.ValidationError("The inventory manager does not belong to an organization.")

        validated_data['created_by'] = request_user
        validated_data['updated_by'] = request_user

        with transaction.atomic():
            nurse, created = CustomUser.objects.get_or_create(
                email=nurse_data.get('email'),
                defaults={
                    "first_name": nurse_data.get('first_name'),
                    "last_name": nurse_data.get('last_name'),
                    "phone_number": nurse_data.get('phone_number'),
                    "role": nurse_data.get('role'),
                    "is_first_time_login": True,
                    "created_by": request_user,
                    "updated_by": request_user
                }
            )

            if created:
                random_password = get_random_string(10)
                nurse.set_password(random_password)
                nurse.save()
                send_registration_email(nurse, random_password)

            return Nurse.objects.create(
                user=nurse,
                organization=inventory_manager.organization,
                inventory_manager=inventory_manager,
                created_by=request_user,
                updated_by=request_user
            )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['nurse'] = UserListSerializer(instance.user).data
        return data


class NurseDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id','first_name', 'last_name', 'email', 'phone_number','created_by','updated_by']
        extra_kwargs = {'id': {'read_only': True},
                        'email': {'read_only': True},
                        'created_by': {'read_only': True},
                        'updated_by': {'read_only': True}}


class OrgInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrgInventory
        fields = ['id','quantity_in_stock','inventory','organization','created_by','updated_by']
        extra_kwargs = {'id': {'read_only': True},
                        'organization': {'read_only': True},
                        'created_by': {'read_only': True},
                        'updated_by': {'read_only': True}}


class AvailableSupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id','first_name', 'last_name']
        extra_kwargs = {'id': {'read_only': True},}


class SupplierInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = ['id','name','category','unit_price','quantity','is_reusable']
        extra_kwargs = {'id': {'read_only': True},}
