# serializers.py
# =============================================================================
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    UserProfile, Location, Department, Product,
    Device, Cart, CartItem, Order, OrderItem
)
from decimal import Decimal
from django.db import IntegrityError
from django.core.exceptions import ValidationError

# =============================================================================
# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'username']


# =============================================================================
# UserProfile Serializer
# =============================================================================
class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'first_name' , 'last_name', 'email' , 'username', 'password', 'phone_number', 'carrier', 'monthly_payment']

    def get_user(self, obj):
        if obj.user:
            return {
                'id': obj.user.id,
                'first_name': obj.user.first_name,
                'last_name': obj.user.last_name,
                'email': obj.user.email,
                'username': obj.user.username,
            }
        return None

    def update(self, instance, validated_data):
        # Pop user data from validated_data to update the user separately
        user_data = validated_data.pop('user', {})
        
        # Update UserProfile fields (e.g., phone_number, carrier, etc.)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Update the related User object fields
        user = instance.user
        user.first_name = user_data.get('first_name', user.first_name)
        user.last_name = user_data.get('last_name', user.last_name)
        user.email = user_data.get('email', user.email)
        user.save()  # Save the updated User fields

        # Save the updated UserProfile instance
        instance.save()

        return instance

    def validate_phone_number(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("Please enter a valid phone number.")
        return value

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')

        try:
            # Create the User
            user = User.objects.create_user(username=username, password=password)

            # Retrieve the automatically created UserProfile
            user_profile = user.profile

            # Update the UserProfile with remaining validated data
            for attr, value in validated_data.items():
                setattr(user_profile, attr, value)
            user_profile.save()

        except IntegrityError:
            raise serializers.ValidationError({"username": "A user with that username already exists. Please log in instead."})

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
            'discount_amount', 'discount_percentage', 'sale_start', 'sale_end',
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
            'discount_amount', 'discount_percentage', 'sale_start', 'sale_end',
            'created_at', 'updated_at'
        ]

# =============================================================================
# CartItem Serializer
# =============================================================================
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    device = DeviceSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True,
        required=False,
        allow_null=True
    )
    device_id = serializers.PrimaryKeyRelatedField(
        queryset=Device.objects.all(),
        source='device',
        write_only=True,
        required=False,
        allow_null=True
    )
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    effective_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    cart = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    class Meta:
        model = CartItem
        fields = [
            'id', 'cart', 'product', 'device',
            'product_id', 'device_id',
            'quantity', 'price', 'override_price',
            'effective_price', 'created_at', 'updated_at'
        ]

    def validate(self, attrs):
        product = attrs.get('product')
        device = attrs.get('device')

        if not product and not device:
            raise serializers.ValidationError("Either 'product_id' or 'device_id' must be provided.")
        if product and device:
            raise serializers.ValidationError("Only one of 'product_id' or 'device_id' can be provided.")
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user

        if not user.is_authenticated:
            raise serializers.ValidationError("User must be authenticated to add items to the cart.")

        try:
            cart = Cart.objects.get(user=user.profile)
        except Cart.DoesNotExist:
            cart = Cart.objects.create(user=user.profile)

        validated_data['cart'] = cart

        product = validated_data.get('product')
        device = validated_data.get('device')

        if product:
            price = product.discounted_price
        elif device:
            price = device.discounted_repair_price
        else:
            raise serializers.ValidationError("Cannot determine price without product or device.")

        validated_data['price'] = price
        # validated_data['effective_price'] = price  # Adjust as per business logic

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
    product = ProductSerializer(read_only=True)
    device = DeviceSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product', write_only=True, required=False, allow_null=True)
    device_id = serializers.PrimaryKeyRelatedField(queryset=Device.objects.all(), source='device', write_only=True, required=False, allow_null=True)
    tax_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'device', 'product_id', 'device_id', 'order', 'quantity', 'price', 'tax_amount']

    def validate(self, attrs):
        product = attrs.get('product')
        device = attrs.get('device')

        if not product and not device:
            raise serializers.ValidationError("Either 'product_id' or 'device_id' must be provided.")
        if product and device:
            raise serializers.ValidationError("Only one of 'product_id' or 'device_id' can be provided.")
        return attrs

# =============================================================================
# Order Serializer
# =============================================================================
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, required=False)
    user = serializers.ReadOnlyField(source='user.user.username')
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_tax = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total', 'total_tax', 'items', 'created_at', 'updated_at']