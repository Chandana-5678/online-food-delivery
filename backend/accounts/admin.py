from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Address, User

@admin.register(User)
class AppUserAdmin(UserAdmin):
    model = User; ordering = ("email",); list_display = ("email", "first_name", "role", "is_active", "is_staff")
    search_fields = ("email", "first_name", "last_name", "phone"); list_filter = ("role", "is_active", "is_staff")
    fieldsets = UserAdmin.fieldsets + (("FoodFlow", {"fields": ("phone", "role", "profile_image")}),)
    add_fieldsets = ((None, {"fields": ("email", "password1", "password2", "role", "phone")}),)

admin.site.register(Address)
