# =============================================================================
# Tests for Device URLs
# =============================================================================
# tests/test_device_urls.py

import pytest
from cart.factories import (
    DeviceFactory,
    UserFactory,
)
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestDeviceURLs:
    """
    Test suite for Device URLs and their responses.
    """

    def setup_method(self):
        """
        Setup method to initialize the APIClient and authenticate a user.
        """
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)

    def test_device_list_url(self):
        """
        Test that the device list URL returns a 200 OK status.
        """
        url = reverse('device-list')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_device_detail_url(self):
        """
        Test that the device detail URL returns a 200 OK status for an existing device.
        """
        device = DeviceFactory(owner=self.user)
        url = reverse('device-detail', args=[device.id])
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == device.id

    def test_device_detail_url_not_found(self):
        """
        Test that the device detail URL returns a 404 Not Found status for a non-existent device.
        """
        url = reverse('device-detail', args=[9999])  # Assuming 9999 does not exist
        response = self.client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
