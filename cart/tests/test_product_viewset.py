# =============================================================================
# Tests for the Product ViewSet
# =============================================================================

import pytest
from cart.factories import LocationFactory, DepartmentFactory, ProductFactory
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from cart.factories import LocationFactory, DepartmentFactory, ProductFactory


@pytest.mark.django_db
class TestProductViewSet:
    """
    Test suite for the ProductViewSet.
    """

    def setup_method(self):
        """
        Initialize the APIClient and set up the URL for the tests.
        """
        self.client = APIClient()
        self.url = reverse('product-list')

    def test_get_products(self):
        """
        Test retrieving a list of products.
        """
        ProductFactory.create_batch(2)
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_create_product(self):
        """
        Test creating a new product.
        """
        location = LocationFactory()
        department = DepartmentFactory()

        data = {
            'name': 'New Product',
            'price': '499.99',
            'description': 'This is a great product',
            'location': location.id,
            'department': department.id,
            'is_available': True
        }

        response = self.client.post(self.url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Product'

    def test_invalid_create_product(self):
        """
        Test that creating a product with invalid data returns an error.
        """
        location = LocationFactory()
        department = DepartmentFactory()

        # Missing required fields
        data = {'name': '', 'price': '-100', 'location': location.id, 'department': department.id}
        response = self.client.post(self.url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in response.data
        assert 'price' in response.data
# ================================================================================================
