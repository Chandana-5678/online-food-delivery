from django.urls import path
from .views import ApplyCouponView, CartItemCreateView, CartItemDetailView, CartView
urlpatterns = [path("cart/", CartView.as_view()), path("cart/items/", CartItemCreateView.as_view()),
    path("cart/items/<int:pk>/", CartItemDetailView.as_view()), path("cart/coupon/", ApplyCouponView.as_view())]
