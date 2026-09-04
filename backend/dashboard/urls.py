from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import DashboardView, UserAdminViewSet
router = DefaultRouter(); router.register("users", UserAdminViewSet, basename="admin-users")
urlpatterns = [path("", DashboardView.as_view()), path("", include(router.urls))]
