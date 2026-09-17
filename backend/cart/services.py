from django.db import transaction
from rest_framework.exceptions import ValidationError
from .models import Cart, CartItem


@transaction.atomic
def add_item(customer, food, quantity, replace=False):
    if quantity < 1: raise ValidationError("Quantity must be at least 1.")
    if not food.is_available or not food.restaurant.is_active: raise ValidationError("This item is currently unavailable.")
    cart, _ = Cart.objects.select_for_update().get_or_create(customer=customer)
    if cart.restaurant_id and cart.restaurant_id != food.restaurant_id:
        if not replace: raise ValidationError({"restaurant_conflict": "Your cart contains food from another restaurant. Confirm replacement with replace=true."})
        cart.items.all().delete(); cart.coupon = None
    cart.restaurant = food.restaurant; cart.save()
    item, created = CartItem.objects.get_or_create(cart=cart, food_item=food, defaults={"quantity": quantity, "unit_price": food.price})
    if not created: item.quantity += quantity; item.unit_price = food.price; item.save()
    return item
