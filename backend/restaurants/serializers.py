from rest_framework import serializers
from .models import Favorite, Restaurant


class RestaurantSerializer(serializers.ModelSerializer):
    is_open = serializers.BooleanField(read_only=True); is_favorite = serializers.SerializerMethodField()
    class Meta: model = Restaurant; fields = "__all__"; read_only_fields = ("owner", "average_rating", "created_at", "updated_at")
    def get_is_favorite(self, obj) -> bool:
        request = self.context.get("request")
        return bool(request and request.user.is_authenticated and Favorite.objects.filter(customer=request.user, restaurant=obj).exists())


class FavoriteSerializer(serializers.ModelSerializer):
    restaurant_detail = RestaurantSerializer(source="restaurant", read_only=True)
    class Meta: model = Favorite; fields = ("id", "restaurant", "restaurant_detail", "created_at"); read_only_fields = ("created_at",)
