from django_filters import rest_framework as filters
from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied
from .models import Category, FoodItem
from .serializers import CategorySerializer, FoodItemSerializer


class FoodFilter(filters.FilterSet):
    min_price = filters.NumberFilter(method="filter_min_price"); max_price = filters.NumberFilter(method="filter_max_price")
    vegetarian = filters.BooleanFilter(field_name="is_vegetarian"); min_rating = filters.NumberFilter(field_name="rating", lookup_expr="gte")
    def filter_min_price(self, qs, name, value): return qs.filter(original_price__gte=value)
    def filter_max_price(self, qs, name, value): return qs.filter(original_price__lte=value)
    class Meta: model = FoodItem; fields = ("category", "restaurant", "is_vegetarian", "is_available")


class OwnerWriteMixin:
    def _check(self, obj):
        restaurant = getattr(obj, "restaurant", obj)
        if restaurant.owner != self.request.user and not self.request.user.is_staff: raise PermissionDenied("You do not own this restaurant.")
    def perform_create(self, serializer): self._check(serializer.validated_data["restaurant"]); serializer.save()
    def perform_update(self, serializer): self._check(serializer.instance); serializer.save()
    def perform_destroy(self, instance): self._check(instance); instance.delete()
    def get_permissions(self): return [permissions.AllowAny()] if self.action in ("list", "retrieve") else [permissions.IsAuthenticated()]


class CategoryViewSet(OwnerWriteMixin, viewsets.ModelViewSet):
    serializer_class = CategorySerializer; filterset_fields = ("restaurant", "is_active"); search_fields = ("name",)
    def get_queryset(self): return Category.objects.select_related("restaurant", "restaurant__owner")


class FoodViewSet(OwnerWriteMixin, viewsets.ModelViewSet):
    serializer_class = FoodItemSerializer; filterset_class = FoodFilter
    search_fields = ("name", "description", "category__name", "restaurant__name")
    ordering_fields = ("original_price", "discount_price", "rating", "popularity", "created_at", "preparation_time")
    def get_queryset(self): return FoodItem.objects.select_related("restaurant", "restaurant__owner", "category")
