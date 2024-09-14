# =============================================================================
# Tests for the Location ViewSet
# =============================================================================
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from cart.factories import LocationFactory

@pytest.mark.django_db
class TestLocationViewSet:
    """
    Test suite for the LocationViewSet.
    """

    def setup_method(self):
        """
        Initialize the APIClient and set up the URL for the tests.
        """
        self.client = APIClient()
        self.url = reverse('location-list')

    def test_get_locations(self):
        """
        Test retrieving a list of locations.
        """
        LocationFactory.create_batch(5)
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 5

    def test_create_location(self):
        """
        Test creating a new location.
        """
        data = {'name': 'New Location', 'description': 'A new storage location'}
        response = self.client.post(self.url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Location'

    def test_invalid_create_location(self):
        """
        Test that creating a location with invalid data returns an error.
        """
        data = {'name': ''}
        response = self.client.post(self.url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in response.data
