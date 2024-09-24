# serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    UserProfile, Location, Department, Product,
    Device, Cart, CartItem, Order, OrderItem
)

# =============================================================================
# UserProfile Serializer
# =============================================================================

# class UserProfileSerializer(serializers.ModelSerializer):
#     username = serializers.CharField(write_only=True)
#     password = serializers.CharField(write_only=True, required=True)
#     email = serializers.EmailField(required=False)
#     user = serializers.PrimaryKeyRelatedField(read_only=True)

#     class Meta:
#         model = UserProfile
#         fields = ['username', 'password', 'email', 'phone_number', 'carrier', 'monthly_payment', 'user']

#     def validate_username(self, value):
#         if User.objects.filter(username=value).exists():
#             raise serializers.ValidationError('A user with that username already exists.')
#         return value

#     def validate_monthly_payment(self, value):
#         if value is not None and value < 0:
#             raise serializers.ValidationError('Monthly payment must be a positive value.')
#         return value

#     def create(self, validated_data):
#         username = validated_data.pop('username')
#         password = validated_data.pop('password')
#         email = validated_data.pop('email', '')
#         user = User.objects.create_user(username=username, email=email, password=password)
#         user_profile = UserProfile.objects.create(user=user, **validated_data)
#         return user_profile

# =============================================================================

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)  # Keep write-only for user creation
    password = serializers.CharField(write_only=True, required=True)  # Write-only for user creation
    email = serializers.EmailField(required=False)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    # Include username as a read-only field from the related User model
    user_username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = UserProfile
        fields = ['username', 'password', 'email', 'phone_number', 'carrier', 'monthly_payment', 'user', 'user_username']

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('A user with that username already exists.')
        return value

    def validate_monthly_payment(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError('Monthly payment must be a positive value.')
        return value

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        email = validated_data.pop('email', '')
        user = User.objects.create_user(username=username, email=email, password=password)
        user_profile = UserProfile.objects.create(user=user, **validated_data)
        return user_profile

# =============================================================================
# Location, Department, and Product Serializers
# =============================================================================

class LocationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Location model.
    """
    class Meta:
        model = Location
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']

class DepartmentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Department model.
    """
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'is_taxable', 'created_at', 'updated_at']

class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the Product model.
    """
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'price', 'description', 'image', 'barcode',
            'location', 'department', 'is_available', 'on_hand', 'cost',
            'created_at', 'updated_at'
        ]

    def validate_price(self, value):
        """
        Validates that the price is a positive number.
        """
        if value < 0:
            raise serializers.ValidationError("Price must be a positive number.")
        return value

# =============================================================================
# Device Serializer
# =============================================================================

class DeviceSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source='owner.username', read_only=True)
    # ... other fields ...

    class Meta:
        model = Device
        fields = [
            'id', 'name', 'device_model', 'repair_price', 'location', 'department',
            'imei', 'serial_number', 'owner', 'image', 'description', 'barcode',
            'defect', 'notes', 'carrier', 'estimated_value', 'passcode',
            'created_at', 'updated_at'
        ]

    def validate_imei(self, value):
        user = self.context['request'].user
        if Device.objects.filter(imei=value, owner=user).exists():
            raise serializers.ValidationError('Device with this IMEI already exists.')
        return value

    def validate_serial_number(self, value):
        user = self.context['request'].user
        if Device.objects.filter(serial_number=value, owner=user).exists():
            raise serializers.ValidationError('Device with this serial number already exists.')
        return value

                
# =============================================================================
# Cart and CartItem Serializers
# =============================================================================

class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the CartItem model.
    Handles serialization of both product and device items.
    """
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
    item_name = serializers.SerializerMethodField()
    effective_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = CartItem
        fields = [
            'id', 'cart', 'product', 'device', 'product_id', 'device_id',
            'item_name', 'quantity', 'override_price', 'effective_price',
            'total_price', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'cart': {'read_only': True},
            'override_price': {'required': False, 'allow_null': True},
        }

    def validate(self, attrs):
        """
        Validates that either product_id or device_id is provided, but not both.
        """
        product = attrs.get('product')
        device = attrs.get('device')

        if not product and not device:
            raise serializers.ValidationError("Either 'product_id' or 'device_id' must be provided.")
        if product and device:
            raise serializers.ValidationError("Only one of 'product_id' or 'device_id' can be provided.")
        return attrs

    def get_item_name(self, obj):
        """
        Returns the name of the associated item (product or device).
        """
        if obj.product:
            return obj.product.name
        elif obj.device:
            return obj.device.name
        return 'Unknown Item'

# =============================================================================

class CartSerializer(serializers.ModelSerializer):
    """
    Serializer for the Cart model.
    Includes nested serialization of CartItems.
    """
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    user = serializers.ReadOnlyField(source='user.username')  # Ensure this line is present

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total', 'created_at', 'updated_at']
        
# =============================================================================
# Order and OrderItem Serializers
# =============================================================================

class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the OrderItem model.
    """
    product_name = serializers.ReadOnlyField(source='product.name')
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'product_name', 'quantity', 'price']

# =============================================================================

class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model.
    Includes nested serialization of OrderItems.
    """
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total', 'items', 'created_at', 'updated_at']

# =============================================================================
# END