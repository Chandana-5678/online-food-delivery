from rest_framework import serializers
from orders.models import Order
from .models import Review
from .services import refresh_ratings
class ReviewSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.get_full_name", read_only=True)
    class Meta: model = Review; fields = "__all__"; read_only_fields = ("customer", "created_at", "updated_at")
    def validate(self, attrs):
        request = self.context["request"]; order = attrs.get("order", getattr(self.instance, "order", None)); restaurant = attrs.get("restaurant", getattr(self.instance, "restaurant", None)); food = attrs.get("food_item", getattr(self.instance, "food_item", None))
        if order.customer_id != request.user.id or order.status != Order.Status.DELIVERED: raise serializers.ValidationError("Only completed orders belonging to you can be reviewed.")
        if restaurant.id != order.restaurant_id: raise serializers.ValidationError("Restaurant does not match the order.")
        if food and not order.items.filter(food_item=food).exists(): raise serializers.ValidationError("Food item was not part of this order.")
        duplicate = Review.objects.filter(customer=request.user, order=order, food_item=food)
        if self.instance: duplicate = duplicate.exclude(pk=self.instance.pk)
        if duplicate.exists(): raise serializers.ValidationError("You have already reviewed this order item.")
        return attrs
    def create(self, data): obj = Review.objects.create(customer=self.context["request"].user, **data); refresh_ratings(obj); return obj
    def update(self, instance, data): obj = super().update(instance, data); refresh_ratings(obj); return obj
