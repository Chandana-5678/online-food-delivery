from datetime import time, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import Address, User
from coupons.models import Coupon
from delivery.models import DeliveryPartner
from menu.models import Category, FoodItem
from notifications.models import Notification
from orders.models import Order, OrderItem, OrderStatusEvent
from payments.models import Payment
from restaurants.models import Restaurant
from reviews.models import Review
from reviews.services import refresh_ratings


class Command(BaseCommand):
    help = "Create idempotent FoodFlow development data"
    def handle(self, *args, **options):
        password = "FoodFlow@123"
        accounts = [
            ("admin@example.com", "Admin", "User", "admin"),
            ("customer@example.com", "Asha", "Rao", "customer"),
            ("customer2@example.com", "Ravi", "Kumar", "customer"),
            ("customer3@example.com", "Meera", "Nair", "customer"),
            ("owner@example.com", "Arjun", "Spice", "restaurant_owner"),
            ("owner2@example.com", "Priya", "Pizza", "restaurant_owner"),
            ("owner3@example.com", "Kabir", "Biryani", "restaurant_owner"),
            ("burger1@example.com", "Maya", "Bliss", "restaurant_owner"),
            ("burger2@example.com", "Rohan", "Grill", "restaurant_owner"),
            ("burger3@example.com", "Sara", "Stack", "restaurant_owner"),
            ("burger4@example.com", "Vikram", "Patty", "restaurant_owner"),
            ("burger5@example.com", "Anika", "Bun", "restaurant_owner"),
            ("delivery@example.com", "Dev", "Rider", "delivery_partner"),
            ("delivery2@example.com", "Neha", "Rider", "delivery_partner"),
        ]
        users = {}
        for email, first, last, role in accounts:
            user, created = User.objects.get_or_create(email=email, defaults={"first_name": first, "last_name": last, "role": role, "phone": "9876543210"})
            user.role = role; user.first_name = first; user.last_name = last; user.phone = "9876543210"; user.is_staff = role == "admin"; user.is_superuser = role == "admin"; user.set_password(password); user.save(); users[email] = user
        for email, vehicle, number, license_no in (("delivery@example.com", "bike", "KA01AB1234", "DL-FF-001"), ("delivery2@example.com", "scooter", "KA02CD5678", "DL-FF-002")):
            DeliveryPartner.objects.update_or_create(user=users[email], defaults={"phone": "9876543210", "vehicle_type": vehicle, "vehicle_number": number, "driving_license_number": license_no, "is_available": True, "rating": 4.7})
        restaurant_data = [("owner@example.com", "Spice Garden", "North Indian, South Indian", "Bengaluru", Decimal("39"), 35),
            ("owner2@example.com", "Pizza Palace", "Pizza, Italian", "Bengaluru", Decimal("49"), 30),
            ("owner3@example.com", "Biryani House", "Biryani, Mughlai", "Bengaluru", Decimal("29"), 40),
            ("burger1@example.com", "Burger Bliss", "Burgers, American", "Bengaluru", Decimal("35"), 25),
            ("burger2@example.com", "Grill & Bun", "Burgers, Grilled", "Bengaluru", Decimal("30"), 28),
            ("burger3@example.com", "Stack Shack", "Burgers, Fast Food", "Bengaluru", Decimal("45"), 32),
            ("burger4@example.com", "Urban Patty", "Gourmet Burgers", "Bengaluru", Decimal("40"), 30),
            ("burger5@example.com", "Bengaluru Burger Co.", "Burgers, Indian Fusion", "Bengaluru", Decimal("25"), 27)]
        restaurants = []
        for owner, name, cuisine, city, fee, eta in restaurant_data:
            obj, _ = Restaurant.objects.update_or_create(name=name, defaults={"owner": users[owner], "description": f"Fresh, flavourful {cuisine} favourites delivered hot.", "phone": "08040001234", "email": owner, "address": "100 Food Street", "city": city, "state": "Karnataka", "postal_code": "560001", "cuisine_type": cuisine, "opening_time": time(0, 0), "closing_time": time(23, 59), "minimum_order": 149, "delivery_fee": fee, "estimated_delivery_time": eta, "average_rating": Decimal("4.5"), "is_active": True}); restaurants.append(obj)
        category_names = ["Biryani", "Pizza", "Burger", "Chinese", "South Indian", "North Indian", "Desserts", "Beverages", "Fast Food", "Seafood"]
        categories = {}
        for i, name in enumerate(category_names):
            restaurant = restaurants[i % 3]; categories[name], _ = Category.objects.get_or_create(restaurant=restaurant, name=name, defaults={"description": f"Popular {name} dishes", "is_active": True})
        foods = [
            ("Chicken Biryani", "Biryani", 299, False), ("Veg Biryani", "Biryani", 229, True), ("Mutton Biryani", "Biryani", 379, False),
            ("Margherita Pizza", "Pizza", 269, True), ("Chicken Pizza", "Pizza", 349, False), ("Farmhouse Pizza", "Pizza", 329, True),
            ("Veg Burger", "Burger", 149, True), ("Chicken Burger", "Burger", 189, False), ("Cheese Burger", "Burger", 179, True),
            ("Fried Rice", "Chinese", 199, True), ("Chicken Noodles", "Chinese", 239, False), ("Chilli Paneer", "Chinese", 249, True),
            ("Masala Dosa", "South Indian", 129, True), ("Idli Vada", "South Indian", 99, True), ("Uttapam", "South Indian", 139, True),
            ("Paneer Butter Masala", "North Indian", 279, True), ("Butter Chicken", "North Indian", 329, False), ("Butter Naan", "North Indian", 59, True),
            ("Gulab Jamun", "Desserts", 99, True), ("Chocolate Brownie", "Desserts", 159, True), ("Kulfi", "Desserts", 109, True),
            ("Mango Lassi", "Beverages", 99, True), ("Cold Coffee", "Beverages", 129, True), ("Fresh Lime Soda", "Beverages", 79, True),
            ("French Fries", "Fast Food", 119, True), ("Chicken Wings", "Fast Food", 249, False), ("Veg Wrap", "Fast Food", 159, True),
            ("Fish Curry", "Seafood", 329, False), ("Prawn Fry", "Seafood", 379, False), ("Fish Fingers", "Seafood", 289, False),
            ("Hyderabadi Biryani", "Biryani", 319, False), ("Pepperoni Pizza", "Pizza", 389, False), ("Schezwan Rice", "Chinese", 219, True),
            ("Rava Dosa", "South Indian", 149, True), ("Dal Makhani", "North Indian", 239, True), ("Falooda", "Desserts", 169, True)]
        for idx, (name, cat, price, veg) in enumerate(foods):
            category = categories[cat]
            FoodItem.objects.update_or_create(restaurant=category.restaurant, name=name, defaults={"category": category, "description": f"Chef-crafted {name} made fresh to order.", "original_price": Decimal(price), "discount_price": Decimal(price - 20) if idx % 3 == 0 else None, "is_vegetarian": veg, "is_available": True, "preparation_time": 15 + idx % 20, "rating": Decimal("4.2") + Decimal(idx % 6) / 10, "popularity": 200 - idx})
        burger_menus = [
            ("Burger Bliss", (("Classic Bliss Burger", 219, False), ("Crispy Veg Burger", 179, True), ("Loaded Cheese Burger", 249, False))),
            ("Grill & Bun", (("Smoky Grilled Burger", 259, False), ("Grilled Paneer Burger", 209, True), ("BBQ Chicken Burger", 279, False))),
            ("Stack Shack", (("Double Stack Burger", 299, False), ("Veggie Stack Burger", 199, True), ("Spicy Stack Burger", 269, False))),
            ("Urban Patty", (("Gourmet Lamb Burger", 349, False), ("Mushroom Melt Burger", 239, True), ("Urban Chicken Burger", 289, False))),
            ("Bengaluru Burger Co.", (("Masala Chicken Burger", 229, False), ("Aloo Tikki Burger", 149, True), ("Paneer Makhani Burger", 219, True))),
        ]
        restaurant_by_name = {restaurant.name: restaurant for restaurant in restaurants}
        for menu_index, (restaurant_name, items) in enumerate(burger_menus):
            restaurant = restaurant_by_name[restaurant_name]
            category, _ = Category.objects.update_or_create(restaurant=restaurant, name="Burger", defaults={"description": "Freshly stacked signature burgers", "is_active": True})
            for item_index, (name, price, vegetarian) in enumerate(items):
                FoodItem.objects.update_or_create(restaurant=restaurant, name=name, defaults={"category": category, "description": f"Freshly grilled {name} served in a toasted bun.", "original_price": Decimal(price), "discount_price": Decimal(price - 20) if item_index == 0 else None, "is_vegetarian": vegetarian, "is_available": True, "preparation_time": 18 + item_index * 3, "rating": Decimal("4.4") + Decimal(menu_index % 4) / 10, "popularity": 180 - menu_index * 10 - item_index})
        for email in ("customer@example.com", "customer2@example.com", "customer3@example.com"):
            Address.objects.update_or_create(customer=users[email], house_number="12A", street="MG Road", defaults={"full_name": users[email].get_full_name(), "phone": "9876543210", "landmark": "Near Metro", "city": "Bengaluru", "state": "Karnataka", "postal_code": "560001", "address_type": "home", "is_default": True})
        now = timezone.now()
        coupon_data = [("WELCOME50", "fixed", 50, 199, 50), ("FEAST20", "percentage", 20, 399, 120), ("PIZZA100", "fixed", 100, 499, 100), ("WEEKEND15", "percentage", 15, 299, 80), ("FREEDEL", "fixed", 49, 249, 49)]
        for code, kind, value, minimum, maximum in coupon_data:
            Coupon.objects.update_or_create(code=code, defaults={"description": f"Save with {code}", "discount_type": kind, "discount_value": value, "minimum_order_amount": minimum, "maximum_discount": maximum, "start_date": now - timedelta(days=1), "expiry_date": now + timedelta(days=365), "usage_limit": 1000, "per_user_limit": 2, "is_active": True})
        demo_statuses = ("delivered", "delivered", "preparing", "ready", "cancelled", "delivered")
        customer_emails = ("customer@example.com", "customer2@example.com", "customer3@example.com")
        for index, status_name in enumerate(demo_statuses, 1):
            customer = users[customer_emails[(index - 1) % 3]]; restaurant = restaurants[(index - 1) % 3]
            address = customer.addresses.first(); food = restaurant.foods.first(); subtotal = food.price * 2
            order, created = Order.objects.get_or_create(order_number=f"FD-20260904-{index:06d}", defaults={"customer": customer, "restaurant": restaurant,
                "delivery_partner": DeliveryPartner.objects.first() if status_name == "delivered" else None, "delivery_address": address,
                "delivery_address_snapshot": {k: getattr(address, k) for k in ("full_name", "phone", "house_number", "street", "landmark", "city", "state", "postal_code")},
                "subtotal": subtotal, "tax": (subtotal * Decimal("0.05")).quantize(Decimal("0.01")), "delivery_fee": restaurant.delivery_fee,
                "discount": 0, "grand_total": subtotal + (subtotal * Decimal("0.05")).quantize(Decimal("0.01")) + restaurant.delivery_fee,
                "payment_method": "cod", "payment_status": "successful" if status_name == "delivered" else "pending", "status": status_name,
                "accepted_at": now - timedelta(minutes=35), "prepared_at": now - timedelta(minutes=20) if status_name in ("ready", "delivered") else None,
                "picked_up_at": now - timedelta(minutes=12) if status_name == "delivered" else None, "delivered_at": now - timedelta(minutes=index) if status_name == "delivered" else None,
                "cancelled_at": now if status_name == "cancelled" else None})
            if created:
                OrderItem.objects.create(order=order, food_item=food, food_name=food.name, quantity=2, unit_price=food.price, subtotal=subtotal)
                OrderStatusEvent.objects.create(order=order, status=status_name, changed_by=customer)
                Payment.objects.create(order=order, customer=customer, amount=order.grand_total, payment_method="cod", status="successful" if status_name == "delivered" else "pending", payment_date=now if status_name == "delivered" else None)
            if status_name == "delivered":
                review, _ = Review.objects.get_or_create(customer=customer, restaurant=restaurant, order=order, food_item=None,
                    defaults={"rating": 4 + index % 2, "comment": "Fresh, well packed and delivered on time."})
                refresh_ratings(review)
            Notification.objects.get_or_create(user=customer, title=f"Order {order.get_status_display()}", message=f"{order.order_number} is {order.get_status_display().lower()}.", defaults={"notification_type": "order"})
        Notification.objects.get_or_create(user=users["customer@example.com"], title="Welcome to FoodFlow", defaults={"message": "Discover great food near you.", "notification_type": "general"})
        self.stdout.write(self.style.SUCCESS(f"Seed complete: {User.objects.count()} users, {Restaurant.objects.count()} restaurants, {FoodItem.objects.count()} foods, {Order.objects.count()} orders."))
