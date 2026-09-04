from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from menu.models import FoodItem
from orders.models import Order
from restaurants.models import Restaurant
class Review(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="reviews")
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE, related_name="reviews", null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(validators=(MinValueValidator(1), MaxValueValidator(5))); comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True); updated_at = models.DateTimeField(auto_now=True)
    class Meta: constraints = [models.UniqueConstraint(fields=("customer", "order", "food_item"), name="unique_order_review")]; ordering = ("-created_at",)
