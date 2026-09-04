from django.contrib import admin
from .models import Category, FoodItem
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin): list_display = ("name", "restaurant", "is_active"); search_fields = ("name", "restaurant__name")
@admin.register(FoodItem)
class FoodAdmin(admin.ModelAdmin):
    list_display = ("name", "restaurant", "category", "original_price", "discount_price", "is_vegetarian", "is_available")
    search_fields = ("name", "restaurant__name"); list_filter = ("is_vegetarian", "is_available", "category")
