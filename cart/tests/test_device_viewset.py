# tests/test_device_viewset.py

import pytest
from cart.factories import (
    DeviceFactory,
    UserFactory,
    LocationFactory,
    DepartmentFactory
)
from cart.models import Device
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status

@pytest.mark.django_db
class TestDeviceViewSet:
    """
    Test suite for the DeviceViewSet.
    """

    def setup_method(self):
        """
        Setup method to initialize the APIClient and authenticate a user.
        """
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
        self.url = reverse('device-list')
        # Create location and department instances
        self.location = LocationFactory()
        self.department = DepartmentFactory()

    def test_get_devices(self):
        """
        Test retrieving the list of devices owned by the authenticated user.
        """
        DeviceFactory.create_batch(3, owner=self.user)
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_create_device(self):
        """
        Test creating a new device.
        """
        url = reverse('device-list')
        data = {
            'name': 'New Device',
            'device_model': 'Model X',
            'repair_price': '100.00',
            'location': self.location.id,
            'department': self.department.id,
            'imei': '123456789012345',
            'serial_number': 'SN123456',
            # Do not include 'owner' in the data
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Device.objects.count() == 1
        device = Device.objects.first()
        assert device.name == 'New Device'
        assert device.owner == self.user  # self.user is the authenticated user

    def test_update_device(self):
        """
        Test updating an existing device.
        """
        device = DeviceFactory(owner=self.user)
        url = reverse('device-detail', args=[device.id])
        data = {'name': 'Updated Device'}
        response = self.client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Updated Device'

    def test_delete_device(self):
        """
        Test deleting a device.
        """
        device = DeviceFactory(owner=self.user)
        url = reverse('device-detail', args=[device.id])
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        # Ensure the device is deleted
        assert not Device.objects.filter(id=device.id).exists()
        