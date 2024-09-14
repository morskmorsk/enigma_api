# =============================================================================
# Tests for Cart and CartItem Serializers
# =============================================================================

# tests/test_cart_serializers.py

from decimal import Decimal
import pytest
from rest_framework.exceptions import ValidationError
from cart.factories import CartFactory, CartItemWithDeviceFactory, CartItemWithProductFactory, DeviceFactory, ProductFactory
from cart.serializers import CartSerializer, CartItemSerializer

@pytest.mark.django_db
class TestCartSerializer:
    """
    Test suite for the CartSerializer.
    """

    def test_cart_serializer(self):
        """
        Test that the CartSerializer serializes the cart correctly.
        """
        cart = CartFactory()
        user = cart.user

        # Add items to the cart
        product = ProductFactory(price=Decimal('100.00'))
        CartItemWithProductFactory(cart=cart, product=product, quantity=2)

        serializer = CartSerializer(cart)
        data = serializer.data

        assert data['user'] == user.username
        assert len(data['items']) == 1
        assert Decimal(data['total']) == cart.total

    def test_cart_serializer_with_no_items(self):
        """
        Test that the CartSerializer handles an empty cart correctly.
        """
        cart = CartFactory()
        serializer = CartSerializer(cart)
        data = serializer.data

        assert data['user'] == cart.user.username
        assert len(data['items']) == 0
        assert Decimal(data['total']) == Decimal('0.00')

@pytest.mark.django_db
class TestCartItemSerializer:
    """
    Test suite for the CartItemSerializer.
    """

    def test_cart_item_serializer_with_product(self):
        """
        Test that the CartItemSerializer serializes a CartItem with a Product correctly.
        """
        cart_item = CartItemWithProductFactory(quantity=3)
        serializer = CartItemSerializer(cart_item)
        data = serializer.data

        assert data['cart'] == cart_item.cart.id
        assert data['quantity'] == 3
        assert data['product']['id'] == cart_item.product.id
        assert data['device'] is None
        assert data['item_name'] == cart_item.product.name
        assert Decimal(data['effective_price']) == cart_item.effective_price
        assert Decimal(data['total_price']) == cart_item.total_price

    def test_cart_item_serializer_with_device(self):
        """
        Test that the CartItemSerializer serializes a CartItem with a Device correctly.
        """
        cart_item = CartItemWithDeviceFactory(quantity=2)
        serializer = CartItemSerializer(cart_item)
        data = serializer.data

        assert data['cart'] == cart_item.cart.id
        assert data['quantity'] == 2
        assert data['device']['id'] == cart_item.device.id
        assert data['product'] is None
        assert data['item_name'] == cart_item.device.name
        assert Decimal(data['effective_price']) == cart_item.effective_price
        assert Decimal(data['total_price']) == cart_item.total_price

    def test_cart_item_serializer_validation(self):
        """
        Test that the CartItemSerializer validates input correctly.
        """
        cart = CartFactory()
        product = ProductFactory()
        device = DeviceFactory()

        # Attempt to create a CartItem with both product_id and device_id
        serializer = CartItemSerializer(data={
            'cart': cart.id,
            'product_id': product.id,
            'device_id': device.id,
            'quantity': 1
        })
        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors
        assert "Only one of 'product_id' or 'device_id' can be provided." in serializer.errors['non_field_errors']

        # Attempt to create a CartItem with neither product_id nor device_id
        serializer = CartItemSerializer(data={
            'cart': cart.id,
            'quantity': 1
        })
        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors
        assert "Either 'product_id' or 'device_id' must be provided." in serializer.errors['non_field_errors']

