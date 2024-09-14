# tests/test_cart_urls.py

import pytest
from django.urls import reverse, resolve

# =============================================================================
# Tests for Cart, CartItem, and Order URLs
# =============================================================================

class TestCartURLs:
    """
    Test suite for Cart, CartItem, and Order URLs.
    """

    def test_cart_list_url(self):
        """
        Test that the cart list URL reverses and resolves correctly.
        """
        url = reverse('cart-list')
        expected_url = '/api/carts/'  # Adjusted to match actual URL
        assert url == expected_url, f"Expected URL '{expected_url}', got '{url}'"
        resolver = resolve(url)
        assert resolver.view_name == 'cart-list'

    def test_cart_item_list_url(self):
        """
        Test that the cart item list URL reverses and resolves correctly.
        """
        url = reverse('cartitem-list')
        expected_url = '/api/cart-items/'  # Adjusted to match actual URL
        assert url == expected_url, f"Expected URL '{expected_url}', got '{url}'"
        resolver = resolve(url)
        assert resolver.view_name == 'cartitem-list'

    def test_order_list_url(self):
        """
        Test that the order list URL reverses and resolves correctly.
        """
        url = reverse('order-list')
        expected_url = '/api/orders/'  # Adjusted to match actual URL
        assert url == expected_url, f"Expected URL '{expected_url}', got '{url}'"
        resolver = resolve(url)
        assert resolver.view_name == 'order-list'