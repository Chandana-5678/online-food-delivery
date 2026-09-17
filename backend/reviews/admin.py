from django.contrib import admin
from .models import Review
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin): list_display = ("customer", "restaurant", "food_item", "rating", "created_at"); list_filter = ("rating", "restaurant"); search_fields = ("customer__email", "comment")
