from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import CouponViewSet
router = DefaultRouter(); router.register("coupons", CouponViewSet, basename="coupon")
urlpatterns = [path("", include(router.urls))]
