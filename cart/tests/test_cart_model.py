# tests/test_cart_models.py

import pytest
from decimal import Decimal
from cart.factories import (
    UserFactory,
    CartFactory,
    CartItemWithProductFactory,
    ProductFactory,
    DeviceFactory,
    CartItemWithDeviceFactory
)

# =============================================================================
# Tests for Cart and CartItem Models
# =============================================================================

@pytest.mark.django_db
class TestCartModel:
    """
    Test suite for the Cart model.
    """

    def test_cart_creation(self):
        """
        Test that a cart is created correctly for a user.
        """
        user = UserFactory()
        cart = CartFactory(user=user)
        assert str(cart) == f"Cart for {cart.user.username}"
        assert cart.total == Decimal('0.00')

    def test_cart_total_with_product_items(self):
        """
        Test that the cart total is calculated correctly when adding product items.
        """
        user = UserFactory()
        cart = CartFactory(user=user)

        # Add a product item to the cart
        product = ProductFactory(price=Decimal('100.00'))
        cart_item = CartItemWithProductFactory(cart=cart, product=product, quantity=2)

        assert cart.total == Decimal('200.00')

    def test_cart_total_with_device_items(self):
        """
        Test that the cart total is calculated correctly when adding device items.
        """
        user = UserFactory()
        cart = CartFactory(user=user)

        # Add a device item to the cart
        device = DeviceFactory(repair_price=Decimal('150.00'))
        cart_item = CartItemWithDeviceFactory(cart=cart, device=device, quantity=1)

        assert cart.total == Decimal('150.00')

    def test_cart_total_with_mixed_items(self):
        """
        Test that the cart total is calculated correctly with both product and device items.
        """
        user = UserFactory()
        cart = CartFactory(user=user)

        # Add a product item
        product = ProductFactory(price=Decimal('50.00'))
        CartItemWithProductFactory(cart=cart, product=product, quantity=2)

        # Add a device item
        device = DeviceFactory(repair_price=Decimal('75.00'))
        CartItemWithDeviceFactory(cart=cart, device=device, quantity=1)

        expected_total = (Decimal('50.00') * 2) + (Decimal('75.00') * 1)
        assert cart.total == expected_total

# =============================================================================
@pytest.mark.django_db
class TestCartItemModel:
    """
    Test suite for the CartItem model.
    """

    def test_cart_item_creation_with_product(self):
        """
        Test that a CartItem associated with a Product is created correctly.
        """
        cart_item = CartItemWithProductFactory(quantity=3)
        product = cart_item.product

        assert cart_item.product == product
        assert cart_item.device is None
        assert str(cart_item) == f"{cart_item.quantity} x {cart_item.product.name}"
        assert cart_item.effective_price == product.price
        assert cart_item.total_price == product.price * cart_item.quantity

    def test_cart_item_creation_with_device(self):
        """
        Test that a CartItem associated with a Device is created correctly.
        """
        cart_item = CartItemWithDeviceFactory(quantity=2)
        device = cart_item.device

        assert cart_item.device == device
        assert cart_item.product is None
        assert str(cart_item) == f"{cart_item.quantity} x {cart_item.device.name}"
        assert cart_item.effective_price == device.repair_price
        assert cart_item.total_price == device.repair_price * cart_item.quantity

    def test_cart_item_effective_price_with_override(self):
        """
        Test that the effective price is overridden correctly.
        """
        cart_item = CartItemWithProductFactory(quantity=1)
        original_price = cart_item.product.price

        # Override the price
        cart_item.override_price = Decimal('80.00')
        cart_item.save()

        assert cart_item.effective_price == Decimal('80.00')
        assert cart_item.effective_price != original_price
