from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    UserProfile, Location, Department, Product,
    Device, Cart, CartItem, Order, OrderItem
)
from decimal import Decimal

# =============================================================================
# UserProfile Serializer
# =============================================================================
class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(write_only=True, required=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'username', 'password', 'email', 'phone_number', 'carrier', 'monthly_payment']

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('A user with that username already exists.')
        return value

    def validate_monthly_payment(self, value):
        if value is not None and value < 5:
            raise serializers.ValidationError('Minimum monthly payment must be greater than $5.00.')
        return value

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        email = validated_data.pop('email')
        user = User.objects.create_user(username=username, password=password, email=email)
        user_profile = UserProfile.objects.get(user=user)
        for attr, value in validated_data.items():
            setattr(user_profile, attr, value)
        user_profile.save()
        return user_profile

# =============================================================================
# Location Serializer
# =============================================================================
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']

# =============================================================================
# Department Serializer
# =============================================================================
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'is_taxable', 'created_at', 'updated_at']

# =============================================================================
# Product Serializer
# =============================================================================
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'price', 'description', 'image', 'barcode',
            'location', 'department', 'is_available', 'on_hand', 'cost',
            'created_at', 'updated_at'
        ]

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price must be a positive number.")
        return value

# =============================================================================
# Device Serializer
# =============================================================================
class DeviceSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source='owner.user.username', read_only=True)
    passcode = serializers.CharField(write_only=True, required=False)
    imei = serializers.CharField(write_only=True, required=False)
    serial_number = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Device
        fields = [
            'id', 'name', 'device_model', 'repair_price', 'location', 'department',
            'imei', 'serial_number', 'owner', 'image', 'description', 'barcode',
            'defect', 'notes', 'carrier', 'estimated_value', 'passcode',
            'created_at', 'updated_at'
        ]

# =============================================================================
# CartItem Serializer
# =============================================================================
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    device = DeviceSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product', write_only=True, required=False, allow_null=True)
    device_id = serializers.PrimaryKeyRelatedField(queryset=Device.objects.all(), source='device', write_only=True, required=False, allow_null=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    effective_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'device', 'product_id', 'device_id', 'quantity', 'price', 'override_price', 'effective_price', 'created_at', 'updated_at']

    def validate(self, attrs):
        product = attrs.get('product')
        device = attrs.get('device')

        if not product and not device:
            raise serializers.ValidationError("Either 'product_id' or 'device_id' must be provided.")
        if product and device:
            raise serializers.ValidationError("Only one of 'product_id' or 'device_id' can be provided.")
        return attrs

    def create(self, validated_data):
        cart = validated_data.get('cart')
        product = validated_data.get('product')
        device = validated_data.get('device')

        # Determine the price based on product or device
        if product:
            price = product.price
        elif device:
            price = device.repair_price or Decimal('0.00')
        else:
            raise serializers.ValidationError("Cannot determine price without product or device.")

        # Set the price in validated data
        validated_data['price'] = price
        return super().create(validated_data)

# =============================================================================
# Cart Serializer
# =============================================================================
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    user = serializers.ReadOnlyField(source='user.user.username')

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total', 'created_at', 'updated_at']

# =============================================================================
# OrderItem Serializer
# =============================================================================
class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.ReadOnlyField(source='product.id')
    device_id = serializers.ReadOnlyField(source='device.id')

    class Meta:
        model = OrderItem
        fields = ['id', 'product_id', 'device_id', 'order', 'quantity', 'price']

# =============================================================================
# Order Serializer
# =============================================================================
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.ReadOnlyField(source='user.user.username')

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total', 'items', 'created_at', 'updated_at']