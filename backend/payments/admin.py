from django.contrib import admin
from .models import Payment
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin): list_display = ("order", "customer", "amount", "payment_method", "status", "payment_date"); list_filter = ("status", "payment_method"); search_fields = ("order__order_number", "transaction_id")
