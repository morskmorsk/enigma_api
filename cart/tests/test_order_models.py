# tests/test_order_models.py

import pytest
from decimal import Decimal
from django.contrib.auth.models import User
from cart.models import Order, OrderItem
from cart.factories import UserFactory, ProductFactory

# =============================================================================
# Tests for the Order and OrderItem Models
# =============================================================================

@pytest.mark.django_db
class TestOrderModel:
    """
    Test suite for the Order model.
    """

    def test_order_creation(self):
        """
        Test that an Order instance is created correctly.
        """
        user = UserFactory()
        order = Order.objects.create(user=user, status='pending', total=Decimal('100.00'))
        expected_str = f"Order {order.id} - {user.username}"
        assert str(order) == expected_str
        assert order.status == 'pending'
        assert order.total == Decimal('100.00')

    def test_order_status_change(self):
        """
        Test that the Order status can be changed and saved correctly.
        """
        user = UserFactory()
        order = Order.objects.create(user=user, status='pending', total=Decimal('200.00'))
        order.status = 'shipped'
        order.save()
        assert order.status == 'shipped'


@pytest.mark.django_db
class TestOrderItemModel:
    """
    Test suite for the OrderItem model.
    """

    def test_order_item_creation(self):
        """
        Test that an OrderItem instance is created correctly.
        """
        user = UserFactory()
        order = Order.objects.create(user=user, status='pending', total=Decimal('300.00'))
        product = ProductFactory(price=Decimal('50.00'))
        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=3,
            price=Decimal('50.00')
        )

        expected_str = f"3 x {product.name} in Order {order.id}"
        assert str(order_item) == expected_str
        assert order_item.price == Decimal('50.00')
        assert order_item.quantity == 3
        