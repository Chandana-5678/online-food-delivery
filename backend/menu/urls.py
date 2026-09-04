from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, FoodViewSet
router = DefaultRouter(); router.register("categories", CategoryViewSet, basename="category"); router.register("foods", FoodViewSet, basename="food")
urlpatterns = [path("", include(router.urls))]
