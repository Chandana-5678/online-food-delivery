from django_filters import rest_framework as filters
from rest_framework import permissions, serializers, viewsets
from rest_framework.exceptions import PermissionDenied
from food_delivery.permissions import IsRestaurantOwner
from .models import Favorite, Restaurant
from .serializers import FavoriteSerializer, RestaurantSerializer


class RestaurantFilter(filters.FilterSet):
    min_rating = filters.NumberFilter(field_name="average_rating", lookup_expr="gte")
    max_delivery_time = filters.NumberFilter(field_name="estimated_delivery_time", lookup_expr="lte")
    max_minimum_order = filters.NumberFilter(field_name="minimum_order", lookup_expr="lte")
    max_delivery_fee = filters.NumberFilter(field_name="delivery_fee", lookup_expr="lte")
    vegetarian = filters.BooleanFilter(method="filter_vegetarian")
    def filter_vegetarian(self, qs, name, value): return qs.filter(foods__is_vegetarian=True).distinct() if value else qs
    class Meta: model = Restaurant; fields = ("cuisine_type", "city", "is_active")


class RestaurantViewSet(viewsets.ModelViewSet):
    serializer_class = RestaurantSerializer; filterset_class = RestaurantFilter
    search_fields = ("name", "cuisine_type", "city", "categories__name", "foods__name"); ordering_fields = ("average_rating", "estimated_delivery_time", "minimum_order", "delivery_fee", "created_at")
    def get_queryset(self):
        qs = Restaurant.objects.select_related("owner")
        return qs if self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.role == "restaurant_owner") else qs.filter(is_active=True)
    def get_permissions(self):
        return [permissions.AllowAny()] if self.action in ("list", "retrieve") else [IsRestaurantOwner()]
    def perform_create(self, serializer):
        if self.request.user.role != "restaurant_owner" and not self.request.user.is_staff: raise PermissionDenied("Restaurant owner role required.")
        serializer.save(owner=self.request.user)
    def perform_update(self, serializer):
        if serializer.instance.owner != self.request.user and not self.request.user.is_staff: raise PermissionDenied("You do not own this restaurant.")
        serializer.save()
    def perform_destroy(self, instance):
        if instance.owner != self.request.user and not self.request.user.is_staff: raise PermissionDenied("You do not own this restaurant.")
        instance.delete()


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer; http_method_names = ("get", "post", "delete", "head", "options")
    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False): return Favorite.objects.none()
        return Favorite.objects.filter(customer=self.request.user).select_related("restaurant")
    def perform_create(self, serializer):
        if self.request.user.role != "customer": raise PermissionDenied("Customer role required.")
        if Favorite.objects.filter(customer=self.request.user, restaurant=serializer.validated_data["restaurant"]).exists(): raise serializers.ValidationError("Restaurant is already a favorite.")
        serializer.save(customer=self.request.user)
