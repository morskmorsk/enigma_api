import pytest
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from cart.models import Cart, CartItem
from decimal import Decimal
from cart.factories import ProductFactory, DeviceFactory

# Test Cart and CartItem models
@pytest.mark.django_db
class TestCartModel:

    def test_cart_creation(self):
        user = User.objects.create_user(username="testuser", password="password")
        cart = Cart.objects.create(user=user)
        assert str(cart) == f"Cart for {cart.user.username}"
        assert cart.total == 0

    def test_cart_total(self):
        user = User.objects.create_user(username="testuser", password="password")
        cart = Cart.objects.create(user=user)

        # Creating a product to add to the cart
        product = ProductFactory(price=Decimal('100.00'))
        content_type = ContentType.objects.get_for_model(product)
        CartItem.objects.create(cart=cart, content_type=content_type, object_id=product.id, quantity=2)

        assert cart.total == Decimal('200.00')

    def test_cart_item_creation(self):
        user = User.objects.create_user(username="testuser", password="password")
        cart = Cart.objects.create(user=user)
        product = ProductFactory(price=Decimal('50.00'))
        content_type = ContentType.objects.get_for_model(product)

        cart_item = CartItem.objects.create(cart=cart, content_type=content_type, object_id=product.id, quantity=3)

        assert str(cart_item) == f"{cart_item.quantity} x {cart_item.content_object}"
        assert cart_item.total_price == Decimal('150.00')


@pytest.mark.django_db
class TestCartItemModel:

    def test_cart_item_effective_price(self):
        user = User.objects.create_user(username="testuser", password="password")
        cart = Cart.objects.create(user=user)
        product = ProductFactory(price=Decimal('200.00'))
        content_type = ContentType.objects.get_for_model(product)

        # Test default price
        cart_item = CartItem.objects.create(cart=cart, content_type=content_type, object_id=product.id, quantity=1)
        assert cart_item.effective_price == Decimal('200.00')

        # Test overridden price
        cart_item.override_price = Decimal('180.00')
        cart_item.save()
        assert cart_item.effective_price == Decimal('180.00')

# /////////////////////////////////////////////////////////////////////////////////////////////
# Test Device serializer
from rest_framework.exceptions import ValidationError
from cart.serializers import CartSerializer, CartItemSerializer
from cart.models import Cart, CartItem
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal
from cart.factories import ProductFactory


@pytest.mark.django_db
class TestCartSerializer:

    def test_cart_serializer(self):
        user = User.objects.create_user(username="testuser", password="password")
        cart = Cart.objects.create(user=user)

        # Create product and cart item
        product = ProductFactory(price=Decimal('100.00'))
        content_type = ContentType.objects.get_for_model(product)
        CartItem.objects.create(cart=cart, content_type=content_type, object_id=product.id, quantity=2)

        # Serialize the cart
        serializer = CartSerializer(cart)
        data = serializer.data

        assert data['user'] == user.id
        assert len(data['items']) == 1
        # Convert the serialized 'total' back to Decimal for comparison
        assert Decimal(data['total']) == cart.total  # Ensure both are compared as Decimal


@pytest.mark.django_db
class TestCartItemSerializer:

    def test_cart_item_serializer(self):
        user = User.objects.create_user(username="testuser", password="password")
        cart = Cart.objects.create(user=user)
        product = ProductFactory(price=Decimal('50.00'))
        content_type = ContentType.objects.get_for_model(product)

        # Create cart item
        cart_item = CartItem.objects.create(cart=cart, content_type=content_type, object_id=product.id, quantity=3)

        # Serialize the cart item
        serializer = CartItemSerializer(cart_item)
        data = serializer.data

        assert data['cart'] == cart.id
        assert data['quantity'] == 3
        # Convert the serialized 'total_price' back to Decimal for comparison
        assert Decimal(data['total_price']) == cart_item.total_price  # Ensure both are compared as Decimal
        
# /////////////////////////////////////////////////////////////////////////////////////////////
# Test Cart viewset
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth.models import User
from cart.models import Cart, CartItem
from cart.factories import ProductFactory
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal
import pytest


@pytest.mark.django_db
class TestCartViewSet:

    def test_list_cart(self):
        client = APIClient()
        user = User.objects.create_user(username="testuser", password="password")
        client.force_authenticate(user=user)

        # Create cart
        cart = Cart.objects.create(user=user)

        # Get cart list
        url = reverse('cart-list')
        response = client.get(url)
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['user'] == user.id

    def test_my_cart(self):
        client = APIClient()
        user = User.objects.create_user(username="testuser", password="password")
        client.force_authenticate(user=user)

        # Create cart
        Cart.objects.create(user=user)

        # Get my cart
        url = reverse('cart-my-cart')
        response = client.get(url)
        assert response.status_code == 200
        assert response.data['user'] == user.id


@pytest.mark.django_db
class TestCartItemViewSet:

    def test_create_cart_item(self):
        client = APIClient()
        user = User.objects.create_user(username="testuser", password="password")
        client.force_authenticate(user=user)

        cart = Cart.objects.create(user=user)
        product = ProductFactory(price=Decimal('50.00'))
        content_type = ContentType.objects.get_for_model(product)

        # Create cart item
        url = reverse('cart-item-list')
        data = {
            'cart': cart.id,
            'content_type': content_type.id,
            'object_id': product.id,
            'quantity': 2
        }
        response = client.post(url, data, format='json')
        assert response.status_code == 201
        assert CartItem.objects.count() == 1
        assert CartItem.objects.first().quantity == 2
        assert CartItem.objects.first().total_price == Decimal('100.00')

# /////////////////////////////////////////////////////////////////////////////////////////////
# Test Cart and cart item urls
from django.urls import reverse, resolve


@pytest.mark.django_db
def test_cart_list_url():
    # Assuming your URL has the /api/ prefix
    assert reverse('cart-list') == '/api/carts/'
    assert resolve('/api/carts/').view_name == 'cart-list'


@pytest.mark.django_db
def test_cart_item_list_url():
    # Assuming your URL has the /api/ prefix
    assert reverse('cart-item-list') == '/api/cart-items/'
    assert resolve('/api/cart-items/').view_name == 'cart-item-list'
