from rest_framework import viewsets, status, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
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
from django.db import IntegrityError
from rest_framework.authtoken.models import Token

import logging

# =============================================================================
logger = logging.getLogger(__name__)

# =============================================================================
def assign_cart_to_user(user_profile):
    cart, created = Cart.objects.get_or_create(user=user_profile)
    return cart

# =============================================================================
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
        try:
            # Validate and save the serializer
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # Get the user instance from the serializer
            user = serializer.instance.user

            # Generate or retrieve the token for the user
            token, _ = Token.objects.get_or_create(user=user)

            # Return the token and a success response
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            logger.error(f"ValidationError: {e.detail}")
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        except KeyError as e:
            logger.error(f"KeyError: Missing field - {str(e)}")
            return Response({"error": f"Missing field: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Unexpected error during signup: {str(e)}", exc_info=True)
            return Response({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Restrict access to cart items belonging to the authenticated user's cart
        return CartItem.objects.filter(cart__user=self.request.user.profile)

    def perform_create(self, serializer):
        serializer.context['request'] = self.request  # Pass the request to the serializer
        serializer.save()
        
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
        # The order total and tax are updated automatically when OrderItems are added

    @action(detail=False, methods=['post'])
    def place_order(self, request):
        profile = get_user_profile(request)
        cart = assign_cart_to_user(profile)
        if not cart.items.exists():
            return Response({'detail': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(user=profile, status='pending')
        for cart_item in cart.items.all():
            order_item = OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                device=cart_item.device,
                quantity=cart_item.quantity,
                price=cart_item.effective_price,
            )
            # Tax calculation is handled in OrderItem's save method

        # Order total and tax are updated automatically
        # Clear the cart
        cart.items.all().delete()
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def user(self, request):
        profile = get_user_profile(request)
        orders = Order.objects.filter(user=profile)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

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

        product = serializer.validated_data.get('product')
        device = serializer.validated_data.get('device')

        if product:
            price = product.discounted_price
        elif device:
            price = device.discounted_repair_price
        else:
            raise ValidationError("Cannot determine price without product or device.")

        serializer.save(price=price)