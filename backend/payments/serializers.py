from rest_framework import serializers
from .models import Payment
class PaymentSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source="order.order_number", read_only=True)
    class Meta: model = Payment; fields = "__all__"; read_only_fields = ("order", "customer", "amount", "payment_method", "transaction_id", "status", "payment_date")
