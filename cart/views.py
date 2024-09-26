from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from .models import (
    UserProfile, Location, Department, Product, Device, Cart, CartItem, Order, OrderItem
)
from .serializers import (
    UserProfileSerializer, LocationSerializer, DepartmentSerializer,
    ProductSerializer, DeviceSerializer, CartSerializer, CartItemSerializer,
    OrderSerializer, OrderItemSerializer
)
from django.contrib.auth.models import User
from decimal import Decimal
from rest_framework.views import APIView

# Helper to assign cart to the user
def assign_cart_to_user(user_profile):
    cart, created = Cart.objects.get_or_create(user=user_profile)
    return cart

def get_user_profile(request):
    try:
        return request.user.profile
    except UserProfile.DoesNotExist:
        raise PermissionDenied("User profile does not exist.")

# =============================================================================
# Signup View
# =============================================================================
class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# =============================================================================
# UserProfile ViewSet
# =============================================================================
class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.is_staff:
            return UserProfile.objects.all()
        return UserProfile.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

# =============================================================================
# Location ViewSet
# =============================================================================
class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

# =============================================================================
# Department ViewSet
# =============================================================================
class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

# =============================================================================
# Product ViewSet
# =============================================================================
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# =============================================================================
# Device ViewSet
# =============================================================================
class DeviceViewSet(viewsets.ModelViewSet):
    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        profile = get_user_profile(self.request)
        return Device.objects.filter(owner=profile)

    def perform_create(self, serializer):
        profile = get_user_profile(self.request)
        serializer.save(owner=profile)

# =============================================================================
# Cart ViewSet
# =============================================================================
class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        profile = get_user_profile(self.request)
        return Cart.objects.filter(user=profile)

    @action(detail=False, methods=['get'])
    def my_cart(self, request):
        profile = get_user_profile(request)
        cart = assign_cart_to_user(profile)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

# =============================================================================
# CartItem ViewSet
# =============================================================================
class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        profile = get_user_profile(self.request)
        return CartItem.objects.filter(cart__user=profile)

    def perform_create(self, serializer):
        profile = get_user_profile(self.request)
        cart = assign_cart_to_user(profile)
        product = serializer.validated_data.get('product')
        device = serializer.validated_data.get('device')

        # Determine price
        if product:
            price = product.price
        elif device:
            price = device.repair_price or Decimal('0.00')
        else:
            raise serializers.ValidationError("Cannot determine price without product or device.")

        serializer.save(cart=cart, price=price)

# =============================================================================
# Order ViewSet
# =============================================================================
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        profile = get_user_profile(self.request)
        return Order.objects.filter(user=profile)

    def perform_create(self, serializer):
        profile = get_user_profile(self.request)
        order = serializer.save(user=profile)
        # Calculate total
        total = sum(item.price * item.quantity for item in order.items.all())
        order.total = total
        order.save()

    @action(detail=False, methods=['post'])
    def place_order(self, request):
        profile = get_user_profile(request)
        cart = assign_cart_to_user(profile)
        if not cart.items.exists():
            return Response({'detail': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(user=profile, status='pending')
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                device=cart_item.device,
                quantity=cart_item.quantity,
                price=cart_item.effective_price,
            )
        # Calculate total
        order.total = sum(item.price * item.quantity for item in order.items.all())
        order.save()
        # Clear the cart
        cart.items.all().delete()
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# =============================================================================
# OrderItem ViewSet
# =============================================================================
class OrderItemViewSet(viewsets.ModelViewSet):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        profile = get_user_profile(self.request)
        return OrderItem.objects.filter(order__user=profile)

    def perform_create(self, serializer):
        profile = get_user_profile(self.request)
        order = serializer.validated_data['order']
        if order.user != profile:
            raise PermissionDenied("You cannot add items to someone else's order.")
        serializer.save()