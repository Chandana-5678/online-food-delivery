from rest_framework.permissions import BasePermission, SAFE_METHODS


class RolePermission(BasePermission):
    roles = ()
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and (request.user.is_superuser or request.user.role in self.roles))


class IsAdmin(RolePermission): roles = ("admin",)
class IsCustomer(RolePermission): roles = ("customer",)
class IsRestaurantOwner(RolePermission): roles = ("restaurant_owner",)
class IsDeliveryPartner(RolePermission): roles = ("delivery_partner",)


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        owner = getattr(obj, "owner", getattr(obj, "customer", None))
        return request.user.is_superuser or owner == request.user
