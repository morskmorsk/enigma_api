# =============================================================================
# Tests for the Department ViewSet
# =============================================================================
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from cart.factories import DepartmentFactory

@pytest.mark.django_db
class TestDepartmentViewSet:
    """
    Test suite for the DepartmentViewSet.
    """

    def setup_method(self):
        """
        Initialize the APIClient and set up the URL for the tests.
        """
        self.client = APIClient()
        self.url = reverse('department-list')

    def test_get_departments(self):
        """
        Test retrieving a list of departments.
        """
        DepartmentFactory.create_batch(3)
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_create_department(self):
        """
        Test creating a new department.
        """
        data = {'name': 'IT Department', 'description': 'Handles tech stuff', 'is_taxable': True}
        response = self.client.post(self.url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'IT Department'

    def test_invalid_create_department(self):
        """
        Test that creating a department with invalid data returns an error.
        """
        data = {'name': ''}
        response = self.client.post(self.url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in response.data
