from decimal import Decimal
from django.conf import settings
from django.db import models
from coupons.models import Coupon
from menu.models import FoodItem
from restaurants.models import Restaurant


class Cart(models.Model):
    customer = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart")
    restaurant = models.ForeignKey(Restaurant, on_delete=models.SET_NULL, null=True, blank=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True); updated_at = models.DateTimeField(auto_now=True)
    @property
    def subtotal(self): return sum((item.subtotal for item in self.items.all()), Decimal("0"))
    @property
    def tax(self):
        from django.conf import settings
        return (self.subtotal * Decimal(str(settings.FOOD_DELIVERY_TAX_PERCENT)) / Decimal("100")).quantize(Decimal("0.01"))
    @property
    def delivery_fee(self): return self.restaurant.delivery_fee if self.restaurant_id else Decimal("0")


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1); unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    class Meta: constraints = [models.UniqueConstraint(fields=("cart", "food_item"), name="unique_cart_food")]
    @property
    def subtotal(self): return self.unit_price * self.quantity
