from rest_framework import serializers
from menu.serializers import FoodItemSerializer
from .models import Cart, CartItem
class CartItemSerializer(serializers.ModelSerializer):
    food = FoodItemSerializer(source="food_item", read_only=True); subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    class Meta: model = CartItem; fields = ("id", "food_item", "food", "quantity", "unit_price", "subtotal"); read_only_fields = ("unit_price",)
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True); subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    tax = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True); delivery_fee = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    class Meta: model = Cart; fields = ("id", "restaurant", "coupon", "items", "subtotal", "tax", "delivery_fee", "created_at", "updated_at")

class AddCartItemSerializer(serializers.Serializer):
    food_item = serializers.IntegerField(); quantity = serializers.IntegerField(min_value=1, default=1); replace = serializers.BooleanField(default=False)

class ApplyCouponSerializer(serializers.Serializer):
    code = serializers.CharField()
