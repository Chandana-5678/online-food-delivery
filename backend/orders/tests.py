from datetime import time, timedelta
from django.utils import timezone
from rest_framework.test import APITestCase
from accounts.models import Address, User
from cart.models import Cart
from coupons.models import Coupon
from delivery.models import DeliveryPartner
from menu.models import Category, FoodItem
from orders.models import Order
from payments.models import Payment
from restaurants.models import Restaurant

class MarketplaceFlowTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer=User.objects.create_user(email="customer@test.com",password="SafePass@123",phone="999",role="customer")
        cls.other=User.objects.create_user(email="other@test.com",password="SafePass@123",phone="999",role="customer")
        cls.owner=User.objects.create_user(email="owner@test.com",password="SafePass@123",phone="999",role="restaurant_owner")
        cls.rider_user=User.objects.create_user(email="rider@test.com",password="SafePass@123",phone="999",role="delivery_partner")
        cls.rider=DeliveryPartner.objects.create(user=cls.rider_user,phone="999",vehicle_number="KA01",driving_license_number="DL01",is_available=True)
        cls.restaurant=Restaurant.objects.create(owner=cls.owner,name="Test Kitchen",description="Great food",phone="999",email="kitchen@test.com",address="Road",city="Bengaluru",state="KA",postal_code="560001",cuisine_type="Indian",opening_time=time(0),closing_time=time(23,59),minimum_order=100,delivery_fee=30,estimated_delivery_time=25)
        cls.category=Category.objects.create(restaurant=cls.restaurant,name="Mains")
        cls.food=FoodItem.objects.create(restaurant=cls.restaurant,category=cls.category,name="Test Biryani",original_price=200,is_vegetarian=False)
        cls.address=Address.objects.create(customer=cls.customer,full_name="Customer",phone="999",house_number="1",street="Road",city="Bengaluru",state="KA",postal_code="560001",is_default=True)
        cls.coupon=Coupon.objects.create(code="TEST20",discount_type="percentage",discount_value=20,minimum_order_amount=100,maximum_discount=50,start_date=timezone.now()-timedelta(days=1),expiry_date=timezone.now()+timedelta(days=1),usage_limit=10,per_user_limit=1)
    def auth(self,user): self.client.force_authenticate(user)
    def add_item(self): self.auth(self.customer); return self.client.post("/api/cart/items/",{"food_item":self.food.id,"quantity":2})
    def place_order(self,payment="cod"): self.add_item(); return self.client.post("/api/orders/",{"delivery_address":self.address.id,"payment_method":payment})
    def test_public_restaurant_and_food_search(self):
        self.assertEqual(self.client.get("/api/restaurants/?search=Kitchen").status_code,200); self.assertEqual(self.client.get("/api/foods/?search=Biryani").data["count"],1)
    def test_customer_cannot_create_restaurant(self):
        self.auth(self.customer); self.assertEqual(self.client.post("/api/restaurants/",{"name":"Nope"}).status_code,403)
    def test_owner_can_create_category_and_food(self):
        self.auth(self.owner); category=self.client.post("/api/categories/",{"restaurant":self.restaurant.id,"name":"Sides","description":"","is_active":True}); self.assertEqual(category.status_code,201)
        food=self.client.post("/api/foods/",{"restaurant":self.restaurant.id,"category":category.data["id"],"name":"Naan","original_price":"50.00","is_vegetarian":True,"is_available":True,"preparation_time":10}); self.assertEqual(food.status_code,201)
    def test_cart_rejects_invalid_quantity(self):
        self.auth(self.customer); self.assertEqual(self.client.post("/api/cart/items/",{"food_item":self.food.id,"quantity":0}).status_code,400)
    def test_coupon_and_order_creation_are_transactional(self):
        self.add_item(); self.assertEqual(self.client.post("/api/cart/coupon/",{"code":"TEST20"}).status_code,200)
        response=self.client.post("/api/orders/",{"delivery_address":self.address.id,"payment_method":"cod"}); self.assertEqual(response.status_code,201); order=Order.objects.get(pk=response.data["id"])
        self.assertEqual(order.items.first().food_name,"Test Biryani"); self.assertEqual(order.items.first().unit_price,200); self.assertEqual(order.discount,50); self.assertFalse(Cart.objects.get(customer=self.customer).items.exists())
    def test_other_customer_cannot_view_order(self):
        order_id=self.place_order().data["id"]; self.auth(self.other); self.assertEqual(self.client.get(f"/api/orders/{order_id}/").status_code,404)
    def test_invalid_status_transition_rejected(self):
        order_id=self.place_order().data["id"]; self.auth(self.owner); self.assertEqual(self.client.post(f"/api/orders/{order_id}/transition/",{"status":"delivered"}).status_code,400)
    def test_full_restaurant_delivery_status_flow(self):
        order_id=self.place_order().data["id"]; self.auth(self.owner)
        for state in ("accepted","preparing","ready"): self.assertEqual(self.client.post(f"/api/orders/{order_id}/transition/",{"status":state}).status_code,200)
        self.auth(self.rider_user); self.assertEqual(self.client.post(f"/api/delivery/{order_id}/accept/",{}).status_code,200)
        for state in ("picked_up","on_the_way","delivered"): self.assertEqual(self.client.post(f"/api/orders/{order_id}/transition/",{"status":state}).status_code,200)
        self.assertEqual(Order.objects.get(pk=order_id).payment_status,"successful")
    def test_mock_online_payment_success(self):
        response=self.place_order("online"); payment=Payment.objects.get(order_id=response.data["id"]); paid=self.client.post(f"/api/payments/{payment.id}/mock-checkout/",{"success":True})
        self.assertEqual(paid.status_code,200); self.assertEqual(paid.data["status"],"successful"); self.assertTrue(paid.data["transaction_id"].startswith("MOCK-"))
    def test_review_requires_delivered_order(self):
        order_id=self.place_order().data["id"]; self.assertEqual(self.client.post("/api/reviews/",{"restaurant":self.restaurant.id,"order":order_id,"rating":5,"comment":"Excellent"}).status_code,400)
    def test_customer_can_cancel_pending(self):
        order_id=self.place_order().data["id"]; self.assertEqual(self.client.post(f"/api/orders/{order_id}/cancel/",{}).status_code,200); self.assertEqual(Order.objects.get(pk=order_id).status,"cancelled")
