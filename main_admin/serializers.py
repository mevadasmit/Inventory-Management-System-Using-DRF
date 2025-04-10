from django.db import transaction
from django.utils.crypto import get_random_string
from rest_framework import serializers
from authentication.models import CustomUser
from base.utils import send_registration_email
from main_admin.models import InventoryCategory, Organization, InventoryManager


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id','first_name','last_name','role','email','phone_number']
        extra_kwargs = {'id': {'read_only': True}}


class InventoryCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryCategory
        fields = ['id','name','created_by','updated_by']
        extra_kwargs = {'id': {'read_only': True},
                        'created_by': {'read_only': True},
                        'updated_by': {'read_only': True}}


class OrganizationSerializer(serializers.ModelSerializer):
    inventory_manager = UserListSerializer(write_only=True)

    class Meta:
        model = Organization
        fields = ['id', 'name', 'email', 'address', 'inventory_manager']
        extra_kwargs = {'id': {'read_only': True}}

    def create(self, validated_data):
        user_data = validated_data.pop('inventory_manager')
        request_user = self.context['request'].user
        validated_data.update(created_by=request_user, updated_by=request_user)

        with transaction.atomic():
            organization = Organization.objects.create(**validated_data)

            inventory_manager, created = CustomUser.objects.get_or_create(
                email=user_data.get('email'),
                defaults={
                    'first_name': user_data.get('first_name'),
                    'last_name': user_data.get('last_name'),
                    'phone_number': user_data.get('phone_number'),
                    'role': user_data.get('role'),
                    'is_first_time_login': True,
                    'created_by': request_user,
                    'updated_by': request_user
                }
            )

            if created:
                password = get_random_string(10)
                inventory_manager.set_password(password)
                inventory_manager.save()
                send_registration_email(inventory_manager, password)
            else:
                inventory_manager.updated_by = request_user
                inventory_manager.save()

            InventoryManager.objects.create(
                user=inventory_manager,
                organization=organization,
                created_by=request_user,
                updated_by=request_user
            )

            return organization

    def to_representation(self, instance):
        data = super().to_representation(instance)
        manager = InventoryManager.objects.filter(organization=instance).first()
        data['inventory_manager'] = UserListSerializer(manager.user).data if manager else None
        return data


class OrganizationDetailSerializer(serializers.ModelSerializer):
    inventory_manager = UserListSerializer(write_only=True)
    class Meta:
        model = Organization
        fields = ['name','email','address','inventory_manager']
        extra_kwargs = {"inventory_manager.id": {"read_only": True},
                        "inventory_manager.role": {"read_only": True},
                        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        manager = InventoryManager.objects.filter(organization=instance).first()
        data['inventory_manager'] = UserListSerializer(manager.user).data if manager else None
        return data