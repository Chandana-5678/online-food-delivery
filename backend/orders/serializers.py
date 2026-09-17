from rest_framework import serializers
from accounts.models import Address
from .models import Order, OrderItem, OrderStatusEvent
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta: model = OrderItem; fields = "__all__"
class OrderStatusEventSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source="get_status_display", read_only=True)
    class Meta: model = OrderStatusEvent; fields = ("id", "status", "label", "created_at")
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True); status_events = OrderStatusEventSerializer(many=True, read_only=True)
    restaurant_name = serializers.CharField(source="restaurant.name", read_only=True); status_label = serializers.CharField(source="get_status_display", read_only=True)
    class Meta: model = Order; fields = "__all__"; read_only_fields = tuple(f.name for f in Order._meta.fields)
class OrderCreateSerializer(serializers.Serializer):
    delivery_address = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all()); payment_method = serializers.ChoiceField(choices=("cod", "online")); customer_notes = serializers.CharField(required=False, allow_blank=True)
    def validate_delivery_address(self, value):
        if value.customer_id != self.context["request"].user.id: raise serializers.ValidationError("Invalid delivery address.")
        return value
