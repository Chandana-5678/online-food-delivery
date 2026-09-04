from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import MockCheckoutView, PaymentViewSet
router = DefaultRouter(); router.register("payments", PaymentViewSet, basename="payment")
urlpatterns = [path("", include(router.urls)), path("payments/<int:pk>/mock-checkout/", MockCheckoutView.as_view())]
