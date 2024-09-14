# tests/test_device_serializer.py

import pytest
from rest_framework.test import APIRequestFactory
from cart.factories import (
    DeviceFactory,
    UserFactory,
    LocationFactory,
    DepartmentFactory
)
from cart.serializers import DeviceSerializer

# =============================================================================
# Tests for the Device Serializer
# =============================================================================

@pytest.mark.django_db
class TestDeviceSerializer:
    """
    Test suite for the DeviceSerializer.
    """

    def test_valid_device_serializer(self):
        """
        Test that the DeviceSerializer serializes data correctly.
        """
        device = DeviceFactory()
        assert device.owner is not None, "DeviceFactory did not assign an owner."
        serializer = DeviceSerializer(instance=device)
        print(serializer.data)  # For debugging
        assert 'owner' in serializer.data, "Serializer data does not contain 'owner' field."
        assert serializer.data['name'] == device.name
        assert serializer.data['owner'] == device.owner.username

    def test_invalid_device_serializer(self):
        """
        Test that the DeviceSerializer validates data correctly for duplicates.
        """
        user = UserFactory()
        existing_device = DeviceFactory(
            imei='123456789012345',
            serial_number='SN123456',
            owner=user
        )

        # Attempt to create a new device with the same IMEI and serial number
        data = {
            'name': 'New Device',
            'device_model': 'Model X',
            'repair_price': '100.00',
            'location': LocationFactory().id,
            'department': DepartmentFactory().id,
            'imei': '123456789012345',  # Duplicate IMEI
            'serial_number': 'SN123456',  # Duplicate serial number
        }

        # Mock the request to include the user in the context
        factory = APIRequestFactory()
        request = factory.post('/devices/', data, format='json')
        request.user = user
        serializer = DeviceSerializer(data=data, context={'request': request})
        assert not serializer.is_valid()
        assert 'imei' in serializer.errors
        actual_error = str(serializer.errors['imei'][0])
        expected_error = 'Device with this IMEI already exists.'
        assert actual_error == expected_error, f"Expected '{expected_error}', got '{actual_error}'"
        