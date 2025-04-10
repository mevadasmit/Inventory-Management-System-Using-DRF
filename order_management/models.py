from django.db import models
from base.models import BaseModel
from authentication.models import CustomUser
from main_admin.models import InventoryManager
from supplier.models import Inventory


# Create your models here.
class Cart(BaseModel):
    inventory_manager = models.ForeignKey(InventoryManager, on_delete=models.CASCADE,related_name='cart')
    total_products = models.PositiveIntegerField(default=0)
    total_price = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Cart For  {self.inventory_manager.user.first_name} -  {self.inventory_manager.organization.name}"

class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE,related_name='cart_items')
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    supplier = models.ForeignKey(CustomUser,on_delete=models.CASCADE,limit_choices_to={"role":"Supplier"})
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.inventory.unit_price
        super().save(*args, **kwargs)
        self.update_cart_totals()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.update_cart_totals()

    def update_cart_totals(self):
        cart_items = self.cart.cart_items.all()
        self.cart.total_price = sum(item.total_price for item in cart_items)
        self.cart.total_products = cart_items.values("inventory").distinct().count()
        self.cart.save()

    def __str__(self):
        return f"{self.inventory.name} - {self.quantity}"

class Order(BaseModel):

    ORDER_STATUS = [("Pending", "Pending"), ("Confirmed", "Confirmed"),
                ("Delivered", "Delivered") , ("Cancelled", "Cancelled")]
    supplier = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={"role": "Supplier"})
    inventory_manager = models.ForeignKey(InventoryManager, on_delete=models.CASCADE, related_name='orders')
    total_price = models.PositiveIntegerField(default=0)
    total_products = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default="Pending")
    confirmed_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    confirmed_by = models.ForeignKey(CustomUser,null=True,blank=True,on_delete=models.CASCADE,related_name='confirmed_by')
    delivered_by = models.ForeignKey(CustomUser,null=True,blank=True, on_delete=models.CASCADE, related_name='delivered_by')

    def update_totals(self):
        self.total_price = sum(item.total_price for item in self.order_items.all())
        self.total_products =self.order_items.count()
        self.save()

    def __str__(self):
        return f"Order {self.id} -  {self.inventory_manager.user.first_name}"

class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,related_name='order_items')
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.PositiveIntegerField(default=0)
    total_price = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        self.order.update_totals()

    def delete(self,*args, **kwargs):
        super().delete(*args, **kwargs)
        self.order.update_totals()

    def __str__(self):
        return f"{self.inventory.name} - {self.quantity}"



