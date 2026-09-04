from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Address, User
from .serializers import AddressSerializer, ForgotPasswordSerializer, LoginSerializer, LogoutSerializer, PasswordChangeSerializer, RegistrationSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all(); serializer_class = RegistrationSerializer; permission_classes = [permissions.AllowAny]


class LoginView(TokenObtainPairView): serializer_class = LoginSerializer


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    def get_object(self): return self.request.user


class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    def post(self, request):
        try: RefreshToken(request.data["refresh"]).blacklist()
        except Exception: return Response({"detail": "Invalid refresh token."}, status=400)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordChangeView(generics.GenericAPIView):
    serializer_class = PasswordChangeSerializer
    def post(self, request):
        serializer = self.get_serializer(data=request.data); serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"]); request.user.save()
        return Response({"detail": "Password changed successfully."})


class ForgotPasswordView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ForgotPasswordSerializer
    def post(self, request):
        user = User.objects.filter(email=request.data.get("email", "").lower()).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk)); token = default_token_generator.make_token(user)
            send_mail("FoodFlow password reset", f"Reset token: {uid}/{token}", None, [user.email])
        return Response({"detail": "If the account exists, reset instructions have been sent."})


class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False): return Address.objects.none()
        return Address.objects.filter(customer=self.request.user)
    def perform_create(self, serializer): serializer.save(customer=self.request.user)
    @action(detail=True, methods=["post"])
    def set_default(self, request, pk=None):
        address = self.get_object(); address.is_default = True; address.save(); return Response(self.get_serializer(address).data)
