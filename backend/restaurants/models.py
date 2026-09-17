from django.conf import settings
from django.db import models
from django.utils import timezone


class Restaurant(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="restaurants")
    name = models.CharField(max_length=160, db_index=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to="restaurants/logos/", blank=True)
    cover_image = models.ImageField(upload_to="restaurants/covers/", blank=True)
    phone = models.CharField(max_length=20); email = models.EmailField()
    address = models.CharField(max_length=255); city = models.CharField(max_length=100, db_index=True)
    state = models.CharField(max_length=100); postal_code = models.CharField(max_length=20)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    cuisine_type = models.CharField(max_length=120, db_index=True)
    opening_time = models.TimeField(); closing_time = models.TimeField()
    minimum_order = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estimated_delivery_time = models.PositiveIntegerField(default=30, help_text="Minutes")
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True); updated_at = models.DateTimeField(auto_now=True)
    class Meta: ordering = ("-average_rating", "name")
    @property
    def is_open(self):
        now = timezone.localtime().time()
        if not self.is_active: return False
        if self.opening_time <= self.closing_time: return self.opening_time <= now <= self.closing_time
        return now >= self.opening_time or now <= self.closing_time
    def __str__(self): return self.name


class Favorite(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorites")
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: constraints = [models.UniqueConstraint(fields=("customer", "restaurant"), name="unique_favorite")]
