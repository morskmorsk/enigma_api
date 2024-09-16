# views.py

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied

from .models import (
    UserProfile, Location, Department, Product,
    Device, Cart, CartItem, Order, OrderItem
)
from .serializers import (
    UserProfileSerializer, LocationSerializer, DepartmentSerializer,
    ProductSerializer, DeviceSerializer, CartSerializer, CartItemSerializer,
    OrderSerializer, OrderItemSerializer
)
from django.contrib.auth.models import User

# =============================================================================

class SignupViewSet(viewsets.ViewSet):
    """
    ViewSet for user signup.
    """
    permission_classes = [AllowAny]

    def create(self, request):
        serializer = UserProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# =============================================================================
# UserProfile ViewSet
# =============================================================================

class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user profiles.
    """
    serializer_class = UserProfileSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """
        Users can only see their own profile.
        """
        return UserProfile.objects.filter(user=self.request.user)
        
    def destroy(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

# =============================================================================
# Location, Department, and Product ViewSets
# =============================================================================

class LocationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing locations.
    """
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

class DepartmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing departments.
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing products.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# =============================================================================
# Device ViewSet
# =============================================================================

class DeviceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing devices owned by users.
    """
    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Returns devices owned by the authenticated user.
        """
        return Device.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        """
        Automatically sets the device's owner to the authenticated user.
        """
        serializer.save(owner=self.request.user)

# =============================================================================
# Cart and CartItem ViewSets
# =============================================================================

class CartViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user carts.
    """
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Users can only see their own cart.
        """
        return Cart.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def my_cart(self, request):
        """
        Custom action to retrieve the authenticated user's cart.
        """
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

class CartItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing items in a user's cart.
    """
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retrieves cart items belonging to the authenticated user's cart.
        """
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return CartItem.objects.filter(cart=cart)

    def perform_create(self, serializer):
        """
        Associates the cart item with the authenticated user's cart.
        """
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)

    def perform_update(self, serializer):
        """
        Ensures the cart item belongs to the authenticated user's cart when updating.
        """
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)

# =============================================================================
# Order and OrderItem ViewSets
# =============================================================================

class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing orders.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Users can only see their own orders.
        """
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Automatically sets the user to the authenticated user when creating an order.
        """
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """
        Custom action to update the status of an order.
        """
        order = self.get_object()
        status = request.data.get('status')
        if status in dict(Order.STATUS_CHOICES):
            order.status = status
            order.save()
            return Response({'status': 'Order status updated', 'new_status': order.status})
        return Response({'error': 'Invalid status'}, status=400)

class OrderItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing items within an order.
    """
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Users can only see order items from their own orders.
        """
        return OrderItem.objects.filter(order__user=self.request.user)

    def perform_create(self, serializer):
        """
        Ensures that the order item is added to the authenticated user's order.
        """
        order = serializer.validated_data['order']
        if order.user != self.request.user:
            raise PermissionDenied("You cannot add items to someone else's order.")
        serializer.save()
