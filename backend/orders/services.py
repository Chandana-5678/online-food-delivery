from decimal import Decimal
from uuid import uuid4
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from cart.models import Cart
from coupons.models import CouponUsage
from coupons.services import validate_coupon
from payments.models import Payment
from notifications.services import notify
from .models import Order, OrderItem, OrderStatusEvent


@transaction.atomic
def create_order(customer, address, payment_method, notes=""):
    cart = Cart.objects.select_for_update().select_related("restaurant", "coupon").prefetch_related("items__food_item").filter(customer=customer).first()
    if not cart or not cart.items.exists(): raise ValidationError("Your cart is empty.")
    if address.customer_id != customer.id: raise ValidationError("Invalid delivery address.")
    if not cart.restaurant.is_active: raise ValidationError("Restaurant is inactive.")
    if cart.subtotal < cart.restaurant.minimum_order: raise ValidationError(f"Minimum order is {cart.restaurant.minimum_order}.")
    for item in cart.items.all():
        if not item.food_item.is_available or item.food_item.restaurant_id != cart.restaurant_id: raise ValidationError(f"{item.food_item.name} is unavailable.")
    discount = Decimal("0"); coupon = None
    if cart.coupon_id: coupon, discount = validate_coupon(cart.coupon.code, customer, cart.subtotal)
    grand_total = cart.subtotal + cart.tax + cart.delivery_fee - discount
    number = f"FD-{timezone.localdate():%Y%m%d}-{uuid4().hex[:6].upper()}"
    address_snapshot = {k: getattr(address, k) for k in ("full_name", "phone", "house_number", "street", "landmark", "city", "state", "postal_code")}
    order = Order.objects.create(order_number=number, customer=customer, restaurant=cart.restaurant, delivery_address=address,
        delivery_address_snapshot=address_snapshot, subtotal=cart.subtotal, tax=cart.tax, delivery_fee=cart.delivery_fee,
        discount=discount, grand_total=grand_total, coupon=coupon, payment_method=payment_method, customer_notes=notes)
    OrderItem.objects.bulk_create([OrderItem(order=order, food_item=i.food_item, food_name=i.food_item.name,
        quantity=i.quantity, unit_price=i.unit_price, subtotal=i.subtotal) for i in cart.items.all()])
    OrderStatusEvent.objects.create(order=order, status=order.status, changed_by=customer)
    Payment.objects.create(order=order, customer=customer, amount=grand_total, payment_method=payment_method)
    if coupon: CouponUsage.objects.create(coupon=coupon, user=customer, order_number=number)
    cart.items.all().delete(); cart.restaurant = None; cart.coupon = None; cart.save()
    notify(customer, "Order placed successfully", f"Your order {number} has been placed.")
    notify(order.restaurant.owner, "New order", f"New order {number} requires attention.")
    return order
