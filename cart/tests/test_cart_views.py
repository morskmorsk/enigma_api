# =============================================================================
# Tests for Cart and CartItem ViewSets
# =============================================================================
# tests/test_cart_views.py

from decimal import Decimal
import pytest
from rest_framework.test import APIClient
from django.urls import reverse

from cart.factories import CartFactory, CartItemWithDeviceFactory, CartItemWithProductFactory, DeviceFactory, ProductFactory, UserFactory
from cart.models import CartItem

@pytest.mark.django_db
class TestCartViewSet:
    """
    Test suite for the CartViewSet.
    """

    def test_list_cart(self):
        """
        Test that a user can list their carts.
        """
        client = APIClient()
        user = UserFactory()
        client.force_authenticate(user=user)

        # Create a cart for the user
        cart = CartFactory(user=user)

        url = reverse('cart-list')
        response = client.get(url)

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['user'] == user.username

    def test_my_cart(self):
        """
        Test that the my_cart action returns the authenticated user's cart.
        """
        client = APIClient()
        user = UserFactory()
        client.force_authenticate(user=user)

        # Ensure the cart exists
        cart = CartFactory(user=user)

        url = reverse('cart-my-cart')
        response = client.get(url)

        assert response.status_code == 200
        assert response.data['user'] == user.username

@pytest.mark.django_db
class TestCartItemViewSet:
    """
    Test suite for the CartItemViewSet.
    """

    def test_create_cart_item_with_product(self):
        """
        Test that a user can add a product to their cart.
        """
        client = APIClient()
        user = UserFactory()
        client.force_authenticate(user=user)

        product = ProductFactory(price=Decimal('50.00'))

        url = reverse('cartitem-list')
        data = {
            'product_id': product.id,
            'quantity': 2
        }
        response = client.post(url, data, format='json')

        assert response.status_code == 201
        cart_item = CartItem.objects.first()
        assert cart_item.quantity == 2
        assert cart_item.product == product
        assert cart_item.device is None
        assert cart_item.total_price == Decimal('100.00')

    def test_create_cart_item_with_device(self):
        """
        Test that a user can add a device to their cart.
        """
        client = APIClient()
        user = UserFactory()
        client.force_authenticate(user=user)

        device = DeviceFactory(repair_price=Decimal('75.00'))

        url = reverse('cartitem-list')
        data = {
            'device_id': device.id,
            'quantity': 1
        }
        response = client.post(url, data, format='json')

        assert response.status_code == 201
        cart_item = CartItem.objects.first()
        assert cart_item.quantity == 1
        assert cart_item.device == device
        assert cart_item.product is None
        assert cart_item.total_price == Decimal('75.00')

    def test_list_cart_items(self):
        """
        Test that a user can list items in their cart.
        """
        client = APIClient()
        user = UserFactory()
        client.force_authenticate(user=user)

        cart = CartFactory(user=user)
        CartItemWithProductFactory(cart=cart)
        CartItemWithDeviceFactory(cart=cart)

        url = reverse('cartitem-list')
        response = client.get(url)

        assert response.status_code == 200
        assert len(response.data) == 2

    def test_delete_cart_item(self):
        """
        Test that a user can delete an item from their cart.
        """
        client = APIClient()
        user = UserFactory()
        client.force_authenticate(user=user)

        cart_item = CartItemWithProductFactory(cart__user=user)

        url = reverse('cartitem-detail', args=[cart_item.id])
        response = client.delete(url)

        assert response.status_code == 204
        assert CartItem.objects.count() == 0

