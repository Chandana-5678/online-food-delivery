from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Address, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "phone", "role", "profile_image", "is_active", "date_joined")
        read_only_fields = ("id", "role", "is_active", "date_joined")


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "phone", "role", "password", "confirm_password")
    def validate_role(self, value):
        if value == User.Role.ADMIN: raise serializers.ValidationError("Administrator accounts cannot self-register.")
        return value
    def validate(self, attrs):
        if attrs["password"] != attrs.pop("confirm_password"): raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        if user.role == User.Role.DELIVERY_PARTNER:
            from delivery.models import DeliveryPartner
            DeliveryPartner.objects.create(user=user, phone=user.phone, vehicle_number="PENDING", driving_license_number=f"PENDING-{user.id}")
        return user


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        exclude = ("customer",)


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    def validate_old_password(self, value):
        if not self.context["request"].user.check_password(value): raise serializers.ValidationError("Current password is incorrect.")
        return value

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
