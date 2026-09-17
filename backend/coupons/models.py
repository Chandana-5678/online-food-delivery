from django.conf import settings
from django.db import models


class Coupon(models.Model):
    class DiscountType(models.TextChoices): PERCENTAGE = "percentage", "Percentage"; FIXED = "fixed", "Fixed Amount"
    code = models.CharField(max_length=30, unique=True); description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=12, choices=DiscountType.choices)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    maximum_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    start_date = models.DateTimeField(); expiry_date = models.DateTimeField()
    usage_limit = models.PositiveIntegerField(default=100); per_user_limit = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    def __str__(self): return self.code


class CouponUsage(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.PROTECT, related_name="usages")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="coupon_usages")
    order_number = models.CharField(max_length=32, db_index=True); used_at = models.DateTimeField(auto_now_add=True)
