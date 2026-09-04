from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import AddressViewSet, ForgotPasswordView, LoginView, LogoutView, PasswordChangeView, ProfileView, RegisterView

router = DefaultRouter(); router.register("addresses", AddressViewSet, basename="address")
urlpatterns = [path("register/", RegisterView.as_view()), path("login/", LoginView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()), path("logout/", LogoutView.as_view()),
    path("profile/", ProfileView.as_view()), path("password/change/", PasswordChangeView.as_view()),
    path("password/forgot/", ForgotPasswordView.as_view()), path("", include(router.urls))]
