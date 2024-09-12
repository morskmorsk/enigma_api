# Order and OrderItem models tests
# models tests for Order and OrderItem models
import pytest
from django.contrib.auth.models import User
from cart.models import Order, OrderItem
from cart.factories import ProductFactory
from decimal import Decimal

@pytest.mark.django_db
class TestOrderModel:

    def test_order_creation(self):
        user = User.objects.create_user(username="testuser", password="password")
        order = Order.objects.create(user=user, status='pending', total=Decimal('100.00'))
        assert str(order) == f"Order {order.id} - {user.username}"
        assert order.status == 'pending'
        assert order.total == Decimal('100.00')

    def test_order_status_change(self):
        user = User.objects.create_user(username="testuser", password="password")
        order = Order.objects.create(user=user, status='pending', total=Decimal('200.00'))
        order.status = 'shipped'
        order.save()
        assert order.status == 'shipped'


@pytest.mark.django_db
class TestOrderItemModel:

    def test_order_item_creation(self):
        user = User.objects.create_user(username="testuser", password="password")
        order = Order.objects.create(user=user, status='pending', total=Decimal('300.00'))
        product = ProductFactory(price=Decimal('50.00'))
        order_item = OrderItem.objects.create(order=order, product=product, quantity=3, price=Decimal('50.00'))

        assert str(order_item) == f"3 x {product.name} in Order {order.id}"
        assert order_item.price == Decimal('50.00')
        assert order_item.quantity == 3

# /////////////////////////////////////////////////////////////////////////////////////////////
# serializers tests for Order and OrderItem serializers
from cart.serializers import OrderSerializer, OrderItemSerializer
from cart.models import Order, OrderItem
from cart.factories import ProductFactory
from django.contrib.auth.models import User
from decimal import Decimal
import pytest

@pytest.mark.django_db
class TestOrderSerializer:

    def test_order_serializer(self):
        user = User.objects.create_user(username="testuser", password="password")
        order = Order.objects.create(user=user, status='pending', total=Decimal('200.00'))
        
        product = ProductFactory(price=Decimal('50.00'))
        OrderItem.objects.create(order=order, product=product, quantity=2, price=Decimal('50.00'))
        
        serializer = OrderSerializer(order)
        data = serializer.data

        assert data['user'] == user.username
        assert data['status'] == 'pending'
        assert data['total'] == '200.00'
        assert len(data['items']) == 1

@pytest.mark.django_db
class TestOrderItemSerializer:

    def test_order_item_serializer(self):
        user = User.objects.create_user(username="testuser", password="password")
        order = Order.objects.create(user=user, status='pending', total=Decimal('150.00'))
        
        product = ProductFactory(price=Decimal('50.00'))
        order_item = OrderItem.objects.create(order=order, product=product, quantity=3, price=Decimal('50.00'))

        serializer = OrderItemSerializer(order_item)
        data = serializer.data

        assert data['product'] == product.id
        assert data['quantity'] == 3
        assert data['price'] == '50.00'

# /////////////////////////////////////////////////////////////////////////////////////////////
# views tests for OrderViewSet and OrderItemViewSet
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth.models import User
from cart.models import Order, OrderItem
from cart.factories import ProductFactory
from decimal import Decimal
import pytest

@pytest.mark.django_db
class TestOrderViewSet:

    def test_list_orders(self):
        client = APIClient()
        user = User.objects.create_user(username="testuser", password="password")
        client.force_authenticate(user=user)

        order = Order.objects.create(user=user, status='pending', total=Decimal('100.00'))
        url = reverse('order-list')
        response = client.get(url)

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['total'] == '100.00'

    def test_create_order(self):
        client = APIClient()
        user = User.objects.create_user(username="testuser", password="password")
        client.force_authenticate(user=user)

        url = reverse('order-list')
        data = {
            'total': '200.00',
            'status': 'pending'
        }
        response = client.post(url, data, format='json')

        assert response.status_code == 201
        assert Order.objects.count() == 1
        assert Order.objects.first().total == Decimal('200.00')

    def test_update_order_status(self):
        client = APIClient()
        user = User.objects.create_user(username="testuser", password="password")
        client.force_authenticate(user=user)

        order = Order.objects.create(user=user, status='pending', total=Decimal('150.00'))
        url = reverse('order-update-status', args=[order.id])
        data = {'status': 'shipped'}

        response = client.patch(url, data, format='json')
        assert response.status_code == 200
        order.refresh_from_db()
        assert order.status == 'shipped'


@pytest.mark.django_db
class TestOrderItemViewSet:

    def test_create_order_item(self):
        client = APIClient()
        user = User.objects.create_user(username="testuser", password="password")
        client.force_authenticate(user=user)

        order = Order.objects.create(user=user, status='pending', total=Decimal('300.00'))
        product = ProductFactory(price=Decimal('50.00'))

        # Ensure 'order' is passed correctly in the data
        url = reverse('order-item-list')
        data = {
            'order': order.id,  # Pass the order ID
            'product': product.id,
            'quantity': 3,
            'price': '50.00'
        }

        response = client.post(url, data, format='json')
        assert response.status_code == 201
        assert OrderItem.objects.count() == 1
        assert OrderItem.objects.first().quantity == 3
        assert OrderItem.objects.first().price == Decimal('50.00')

    def test_list_order_items(self):
        client = APIClient()
        user = User.objects.create_user(username="testuser", password="password")
        client.force_authenticate(user=user)

        order = Order.objects.create(user=user, status='pending', total=Decimal('400.00'))
        product = ProductFactory(price=Decimal('100.00'))
        OrderItem.objects.create(order=order, product=product, quantity=2, price=Decimal('100.00'))

        url = reverse('order-item-list')
        response = client.get(url)

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]['quantity'] == 2

# /////////////////////////////////////////////////////////////////////////////////////////////
# urls tests for Order and OrderItem viewsets
from django.urls import reverse, resolve
import pytest

@pytest.mark.django_db
def test_order_list_url():
    assert reverse('order-list') == '/api/orders/'
    assert resolve('/api/orders/').view_name == 'order-list'

@pytest.mark.django_db
def test_order_item_list_url():
    assert reverse('order-item-list') == '/api/order-items/'
    assert resolve('/api/order-items/').view_name == 'order-item-list'
