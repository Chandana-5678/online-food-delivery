from rest_framework import serializers
from .models import DeliveryPartner
class DeliveryPartnerSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    class Meta: model = DeliveryPartner; fields = "__all__"; read_only_fields = ("user", "rating")

class EarningsSerializer(serializers.Serializer):
    completed_deliveries = serializers.IntegerField(); total_earnings = serializers.DecimalField(max_digits=12, decimal_places=2)
