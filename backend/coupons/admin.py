from django.contrib import admin
from .models import Coupon, CouponUsage
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin): list_display = ("code", "discount_type", "discount_value", "expiry_date", "is_active"); search_fields = ("code",); list_filter = ("discount_type", "is_active")
admin.site.register(CouponUsage)
