from rest_framework.test import APITestCase
from .models import User

class AuthenticationTests(APITestCase):
    def test_registration_hashes_password(self):
        response=self.client.post("/api/auth/register/",{"email":"new@example.com","first_name":"New","last_name":"User","phone":"9999999999","role":"customer","password":"SafePass@123","confirm_password":"SafePass@123"})
        self.assertEqual(response.status_code,201); self.assertTrue(User.objects.get(email="new@example.com").check_password("SafePass@123"))
    def test_admin_cannot_self_register(self):
        response=self.client.post("/api/auth/register/",{"email":"bad@example.com","first_name":"Bad","last_name":"Admin","phone":"9999999999","role":"admin","password":"SafePass@123","confirm_password":"SafePass@123"})
        self.assertEqual(response.status_code,400)
    def test_login_returns_jwt_and_user(self):
        User.objects.create_user(email="customer@example.com",password="SafePass@123",phone="9999999999")
        response=self.client.post("/api/auth/login/",{"email":"customer@example.com","password":"SafePass@123"})
        self.assertEqual(response.status_code,200); self.assertIn("access",response.data); self.assertEqual(response.data["user"]["role"],"customer")
    def test_profile_requires_authentication(self): self.assertEqual(self.client.get("/api/auth/profile/").status_code,401)
