# ******************************************************************************************
# serializers.py provides the serializers for the models in the cart app.
# ******************************************************************************************
from venv import logger
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
# =============================================================================
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)  # Make password optional during updates

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'email']
        read_only_fields = ['id', 'username']  # Prevent updates to 'id' and 'username'

    def create(self, validated_data):
        """
        Create a new User instance. Password is required during creation.
        """
        password = validated_data.pop('password', None)
        if not password:
            raise serializers.ValidationError({"password": "Password is required."})

        try:
            user = User(**validated_data)
            user.set_password(password)  # Hash the password
            user.save()
        except IntegrityError:
            raise serializers.ValidationError({
                "username": "A user with that username already exists. Please log in instead."
            })

        return user

    def update(self, instance, validated_data):
        """
        Update an existing User instance. Password is optional.
        """
        password = validated_data.pop('password', None)

        # Update other User fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update password if provided and not empty
        if password:
            instance.set_password(password)

        instance.save()
        return instance


# =============================================================================
# UserProfile Serializer
# =============================================================================
class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'phone_number', 'carrier', 'monthly_payment',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        """
        Create a new UserProfile instance along with the nested User instance.
        """
        user_data = validated_data.pop('user', {})

        # Use the nested UserSerializer to create a User instance
        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        # Create the UserProfile instance
        user_profile = UserProfile.objects.create(user=user, **validated_data)
        return user_profile

    def update(self, instance, validated_data):
        """
        Update an existing UserProfile instance along with the nested User instance.
        """
        user_data = validated_data.pop('user', {})

        # Update UserProfile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update User fields using the nested serializer
        if user_data:
            user_serializer = UserSerializer(instance=instance.user, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        # Save the UserProfile instance
        instance.save()
        return instance


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
# ******************************************************************************************