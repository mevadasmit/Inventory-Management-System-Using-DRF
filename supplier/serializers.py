from rest_framework import serializers
from supplier.models import Inventory


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = ['id','name','supplier','category','quantity','unit_price','is_reusable']
        extra_kwargs = {'supplier': {'read_only': True}}



class InventoryDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = ['id','category','quantity','unit_price','is_reusable']
        extra_kwargs = {'id': {'read_only': True}}


