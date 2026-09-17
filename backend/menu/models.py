from django.db import models
from restaurants.models import Restaurant


class Category(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=120); description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", blank=True); is_active = models.BooleanField(default=True)
    class Meta: ordering = ("name",); constraints = [models.UniqueConstraint(fields=("restaurant", "name"), name="unique_restaurant_category")]
    def __str__(self): return self.name


class FoodItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="foods")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="foods")
    name = models.CharField(max_length=160, db_index=True); description = models.TextField(blank=True)
    image = models.ImageField(upload_to="foods/", blank=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_vegetarian = models.BooleanField(default=True); is_available = models.BooleanField(default=True)
    preparation_time = models.PositiveIntegerField(default=20); rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    popularity = models.PositiveIntegerField(default=0); created_at = models.DateTimeField(auto_now_add=True); updated_at = models.DateTimeField(auto_now=True)
    class Meta: ordering = ("name",)
    @property
    def price(self): return self.discount_price if self.discount_price is not None else self.original_price
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.category_id and self.restaurant_id and self.category.restaurant_id != self.restaurant_id: raise ValidationError("Category must belong to the same restaurant.")
        if self.discount_price is not None and self.discount_price > self.original_price: raise ValidationError("Discount price cannot exceed original price.")
    def __str__(self): return self.name
