from django.contrib import admin
from .models import Order, OrderItem, OrderStatusEvent
class OrderItemInline(admin.TabularInline): model = OrderItem; extra = 0; readonly_fields = ("food_name", "quantity", "unit_price", "subtotal")
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "customer", "restaurant", "status", "payment_status", "grand_total", "created_at")
    search_fields = ("order_number", "customer__email", "restaurant__name"); list_filter = ("status", "payment_status", "payment_method"); inlines = (OrderItemInline,)
admin.site.register(OrderStatusEvent)
