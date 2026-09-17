from rest_framework import serializers
from .models import Category, FoodItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta: model = Category; fields = "__all__"


class FoodItemSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    restaurant_name = serializers.CharField(source="restaurant.name", read_only=True)
    class Meta: model = FoodItem; fields = "__all__"; read_only_fields = ("rating", "popularity", "created_at", "updated_at")
    def validate(self, attrs):
        category = attrs.get("category", getattr(self.instance, "category", None)); restaurant = attrs.get("restaurant", getattr(self.instance, "restaurant", None))
        if category and restaurant and category.restaurant_id != restaurant.id: raise serializers.ValidationError("Category must belong to the selected restaurant.")
        discount = attrs.get("discount_price", getattr(self.instance, "discount_price", None)); original = attrs.get("original_price", getattr(self.instance, "original_price", None))
        if discount is not None and original is not None and discount > original: raise serializers.ValidationError("Discount price cannot exceed original price.")
        return attrs
