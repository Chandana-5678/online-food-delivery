from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied
from .models import Review
from .serializers import ReviewSerializer
from .services import refresh_ratings
class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer; filterset_fields = ("customer", "restaurant", "food_item", "rating"); ordering_fields = ("created_at", "rating")
    def get_queryset(self): return Review.objects.select_related("customer", "restaurant", "food_item", "order")
    def get_permissions(self): return [permissions.AllowAny()] if self.action in ("list", "retrieve") else [permissions.IsAuthenticated()]
    def perform_update(self, serializer):
        if serializer.instance.customer != self.request.user: raise PermissionDenied("You can edit only your review.")
        serializer.save()
    def perform_destroy(self, instance):
        if instance.customer != self.request.user: raise PermissionDenied("You can delete only your review.")
        restaurant, food = instance.restaurant, instance.food_item; instance.delete()
        from django.db.models import Avg
        restaurant.average_rating = restaurant.reviews.aggregate(v=Avg("rating"))["v"] or 0; restaurant.save(update_fields=["average_rating"])
        if food: food.rating = food.reviews.aggregate(v=Avg("rating"))["v"] or 0; food.save(update_fields=["rating"])
