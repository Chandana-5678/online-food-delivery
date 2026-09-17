from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True
    def create_user(self, email, password=None, **extra):
        if not email: raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, username=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, email, password=None, **extra):
        extra.update(is_staff=True, is_superuser=True, role=User.Role.ADMIN)
        return self.create_user(email, password, **extra)


class User(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        RESTAURANT_OWNER = "restaurant_owner", "Restaurant Owner"
        DELIVERY_PARTNER = "delivery_partner", "Delivery Partner"
        ADMIN = "admin", "Administrator"
    email = models.EmailField(unique=True, db_index=True)
    phone = models.CharField(max_length=20)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    profile_image = models.ImageField(upload_to="profiles/", blank=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()
    def save(self, *args, **kwargs):
        self.email = self.email.lower().strip()
        self.username = self.email
        super().save(*args, **kwargs)


class Address(models.Model):
    class Type(models.TextChoices):
        HOME = "home", "Home"
        OFFICE = "office", "Office"
        OTHER = "other", "Other"
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    house_number = models.CharField(max_length=120)
    street = models.CharField(max_length=255)
    landmark = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    address_type = models.CharField(max_length=10, choices=Type.choices, default=Type.HOME)
    is_default = models.BooleanField(default=False)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_default:
            Address.objects.filter(customer=self.customer).exclude(pk=self.pk).update(is_default=False)
    def __str__(self): return f"{self.full_name} - {self.city}"
