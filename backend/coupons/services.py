from decimal import Decimal
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from .models import Coupon


def validate_coupon(code, user, subtotal):
    coupon = Coupon.objects.filter(code__iexact=code).first(); now = timezone.now()
    if not coupon: raise ValidationError("Invalid coupon code.")
    if not coupon.is_active: raise ValidationError("This coupon is inactive.")
    if not coupon.start_date <= now <= coupon.expiry_date: raise ValidationError("This coupon has expired or is not active yet.")
    if subtotal < coupon.minimum_order_amount: raise ValidationError(f"Minimum order is {coupon.minimum_order_amount}.")
    if coupon.usages.count() >= coupon.usage_limit: raise ValidationError("This coupon has reached its usage limit.")
    if coupon.usages.filter(user=user).count() >= coupon.per_user_limit: raise ValidationError("You have already used this coupon.")
    discount = subtotal * coupon.discount_value / Decimal("100") if coupon.discount_type == Coupon.DiscountType.PERCENTAGE else coupon.discount_value
    if coupon.maximum_discount is not None: discount = min(discount, coupon.maximum_discount)
    return coupon, min(discount, subtotal).quantize(Decimal("0.01"))
