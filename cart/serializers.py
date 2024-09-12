# Serializers.py is used to convert complex data types, such as querysets and model instances, to native Python data types that can then be easily rendered into JSON, XML or other content types.
from django.contrib.auth.models import User
import faker
from .models import UserProfile
from rest_framework import serializers


class UserProfileSerializer(serializers.ModelSerializer):
    # Allow the input of username when creating the user profile
    username = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = UserProfile        
        fields = ['user', 'username', 'password', 'email', 'phone_number', 'carrier', 'monthly_payment']
        extra_kwargs = {
            'user': {'read_only': True},  # user field is read-only in response
            'phone_number': {'required': False},
            'carrier': {'required': False},
            'monthly_payment': {'required': False}
        }

    def create(self, validated_data):
        # Extract user-related fields from the validated data
        username = validated_data.pop('username')  # Username is now writable, so we extract it
        password = validated_data.pop('password')
        email = validated_data.pop('email', None)  # Provide a default None if email is not present

        # Create a new User instance, handle the case where email is optional
        user = User.objects.create_user(username=username, password=password, email=email)
        
        # Now create the UserProfile and assign the created User to it
        user_profile = UserProfile.objects.create(user=user, **validated_data)
        user_profile.save()
        return user_profile
    
    def to_representation(self, instance):
        """Customize the representation to include the username in the response."""
        representation = super().to_representation(instance)
        representation['username'] = instance.user.username  # Display the username in the output
        return representation
    
# /////////////////////////////////////////////////////////////////////////////////////////////
from .models import Location, Department, Product

# Location Serializer
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']


# Department Serializer
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'is_taxable', 'created_at', 'updated_at']


# Product Serializer
class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'price', 'description', 'image', 'barcode', 'location', 'department',
            'is_available', 'on_hand', 'cost', 'created_at', 'updated_at'
        ]

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price must be a positive number.")
        return value

# /////////////////////////////////////////////////////////////////////////////////////////////
# device serializer
from .models import Device

class DeviceSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')  # Read-only as it's linked to the user

    class Meta:
        model = Device
        fields = [
            'id', 'owner', 'name', 'device_model', 'repair_price', 'description', 'image', 'barcode', 'imei', 
            'location', 'department', 'serial_number', 'defect', 'notes', 'carrier', 
            'estimated_value', 'passcode', 'created_at', 'updated_at'
        ]

    def validate_imei(self, value):
        # Validate the uniqueness of the 'imei' field if it's provided
        if value and Device.objects.filter(imei=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("A device with this IMEI already exists.")
        return value

    def validate_serial_number(self, value):
        # Validate the uniqueness of the 'serial_number' field if it's provided
        if value and Device.objects.filter(serial_number=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("A device with this serial number already exists.")
        return value

# /////////////////////////////////////////////////////////////////////////////////////////////
# cart/serializers.py
from .models import Cart, CartItem

class CartItemSerializer(serializers.ModelSerializer):
    content_object = serializers.SerializerMethodField()  # To display the related object (Product or Device)
    
    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'content_type', 'object_id', 'content_object', 'quantity', 'override_price', 'effective_price', 'total_price', 'created_at', 'updated_at']
    
    def get_content_object(self, obj):
        return str(obj.content_object)  # Represent the related object (e.g., Product or Device)
    
    def create(self, validated_data):
        content_type = validated_data.pop('content_type')
        object_id = validated_data.pop('object_id')
        content_object = content_type.get_object_for_this_type(id=object_id)
        validated_data['content_object'] = content_object
        return super().create(validated_data)

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total', 'created_at', 'updated_at']

# /////////////////////////////////////////////////////////////////////////////////////////////
from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total', 'items', 'created_at', 'updated_at']