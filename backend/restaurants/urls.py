from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import FavoriteViewSet, RestaurantViewSet
router = DefaultRouter(); router.register("restaurants", RestaurantViewSet, basename="restaurant"); router.register("favorites", FavoriteViewSet, basename="favorite")
urlpatterns = [path("", include(router.urls))]
