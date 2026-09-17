from decimal import Decimal
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from coupons.services import validate_coupon
from menu.models import FoodItem
from .models import Cart, CartItem
from .serializers import AddCartItemSerializer, ApplyCouponSerializer, CartItemSerializer, CartSerializer
from .services import add_item


class CartView(generics.GenericAPIView):
    serializer_class = CartSerializer
    def get(self, request):
        cart, _ = Cart.objects.prefetch_related("items__food_item").get_or_create(customer=request.user)
        data = self.get_serializer(cart).data
        discount = Decimal("0")
        if cart.coupon_id:
            try: _, discount = validate_coupon(cart.coupon.code, request.user, cart.subtotal)
            except ValidationError: cart.coupon = None; cart.save(update_fields=["coupon"])
        data["discount"] = discount; data["grand_total"] = cart.subtotal + cart.tax + cart.delivery_fee - discount
        return Response(data)
    def delete(self, request):
        cart, _ = Cart.objects.get_or_create(customer=request.user); cart.items.all().delete(); cart.restaurant = None; cart.coupon = None; cart.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartItemCreateView(generics.GenericAPIView):
    serializer_class = AddCartItemSerializer
    def post(self, request):
        food = generics.get_object_or_404(FoodItem.objects.select_related("restaurant"), pk=request.data.get("food_item"))
        item = add_item(request.user, food, int(request.data.get("quantity", 1)), bool(request.data.get("replace", False)))
        return Response(CartItemSerializer(item).data, status=201)


class CartItemDetailView(generics.GenericAPIView):
    serializer_class = CartItemSerializer
    def _item(self, request, pk): return generics.get_object_or_404(CartItem, pk=pk, cart__customer=request.user)
    def patch(self, request, pk):
        item = self._item(request, pk); quantity = int(request.data.get("quantity", 0))
        if quantity < 1: raise ValidationError("Quantity must be at least 1.")
        item.quantity = quantity; item.save(); return Response(CartItemSerializer(item).data)
    def delete(self, request, pk): self._item(request, pk).delete(); return Response(status=204)


class ApplyCouponView(generics.GenericAPIView):
    serializer_class = ApplyCouponSerializer
    def post(self, request):
        cart = generics.get_object_or_404(Cart, customer=request.user); coupon, discount = validate_coupon(request.data.get("code", ""), request.user, cart.subtotal)
        cart.coupon = coupon; cart.save(); return Response({"coupon": coupon.code, "discount": discount})
    def delete(self, request):
        Cart.objects.filter(customer=request.user).update(coupon=None); return Response(status=204)
