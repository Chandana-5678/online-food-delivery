from django.contrib import admin
from .models import Favorite, Restaurant
@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "city", "cuisine_type", "average_rating", "is_active")
    search_fields = ("name", "city", "cuisine_type", "owner__email"); list_filter = ("city", "cuisine_type", "is_active")
admin.site.register(Favorite)
