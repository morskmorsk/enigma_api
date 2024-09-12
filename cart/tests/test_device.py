import pytest
from django.core.exceptions import ValidationError
from cart.factories import DeviceFactory
from unittest import mock
from django.core.files.uploadedfile import SimpleUploadedFile


# Test Device model
@pytest.mark.django_db
class TestDeviceModel:

    def test_device_str(self):
        device = DeviceFactory(name="iPhone", device_model="13 Pro")
        assert str(device) == "iPhone (13 Pro) - Owned by {}".format(device.owner.username)

    # def test_device_image_validation(self):
    #     # Test with a valid image (should pass)
    #     valid_image = SimpleUploadedFile("valid_image.jpg", b"file_content", content_type="image/jpeg")
    #     device = DeviceFactory(image=valid_image)
    #     try:
    #         device.clean()  # This should pass with no errors for a valid image
    #     except ValidationError:
    #         pytest.fail("ValidationError raised unexpectedly for a valid image")

    #     # Test with an invalid image file extension (should fail)
    #     invalid_image = SimpleUploadedFile("invalid_file.txt", b"file_content", content_type="text/plain")
    #     device.image = invalid_image
    #     with pytest.raises(ValidationError) as excinfo:
    #         device.clean()
    #     # Check the validation error raised for an invalid image extension
    #     assert excinfo.value.messages == ['Only .jpg, .jpeg, .tiff, .webp and .png files are allowed.']

    #     # Test with an image that exceeds the size limit (should fail)
    #     large_image = SimpleUploadedFile("large_image.jpg", b"file_content" * (6 * 1024 * 1024), content_type="image/jpeg")
    #     device.image = large_image
    #     with pytest.raises(ValidationError) as excinfo:
    #         device.clean()
    #     # Check the validation error raised for exceeding the size limit
    #     assert excinfo.value.messages == ['The image file size cannot exceed 5 MB.']

    # def test_imei_uniqueness(self):
    #     # Create the first device with a unique IMEI
    #     device1 = DeviceFactory(imei="123456789012345")

    #     # Build the second device with the same IMEI and assign the same owner
    #     device2 = DeviceFactory.build(imei="123456789012345", owner=device1.owner)
    #     with pytest.raises(ValidationError) as excinfo:
    #         device2.full_clean()  # Call full_clean to trigger validation
    #     errors = excinfo.value.message_dict
    #     # Check both the '__all__' and 'imei' fields in the error dictionary
    #     assert errors['__all__'] == ['A device with this IMEI already exists.']
    #     assert errors['imei'] == ['Device with this IMEI already exists.']

    # def test_serial_number_uniqueness(self):
    #     # Create the first device with a unique serial number
    #     device1 = DeviceFactory(serial_number="SN123456")

    #     # Build the second device with the same serial number and assign the same owner
    #     device2 = DeviceFactory.build(serial_number="SN123456", owner=device1.owner)
    #     with pytest.raises(ValidationError) as excinfo:
    #         device2.full_clean()  # Call full_clean to trigger validation
    #     errors = excinfo.value.message_dict
    #     # Check both the '__all__' and 'serial_number' fields in the error dictionary
    #     assert errors['__all__'] == ['A device with this serial number already exists.']
    #     assert errors['serial_number'] == ['Device with this Serial Number already exists.']

# /////////////////////////////////////////////////////////////////////////////////////////////
# Test Device Serializer
import pytest
from rest_framework.exceptions import ValidationError
from cart.serializers import DeviceSerializer
from cart.factories import DeviceFactory, LocationFactory, DepartmentFactory

@pytest.mark.django_db
class TestDeviceSerializer:

    def test_valid_device_serializer(self):
        device = DeviceFactory()
        serializer = DeviceSerializer(instance=device)
        assert serializer.data['name'] == device.name

    def test_invalid_device_serializer(self):
        location = LocationFactory()
        department = DepartmentFactory()
        
        # Test invalid imei and serial_number (duplicate)
        device1 = DeviceFactory(imei="123456789012345", serial_number="SN123456")
        
        invalid_data = {
            'name': 'Device 2',
            'owner': device1.owner.id,
            'imei': '123456789012345',  # Duplicate IMEI
            'serial_number': 'SN123456',  # Duplicate Serial Number
            'location': location.id,
            'department': department.id
        }
        
        serializer = DeviceSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert 'imei' in serializer.errors
        assert 'serial_number' in serializer.errors

# /////////////////////////////////////////////////////////////////////////////////////////////
# Test Device viewset
import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from cart.factories import DeviceFactory, UserFactory, LocationFactory, DepartmentFactory

@pytest.mark.django_db
class TestDeviceViewSet:

    def setup_method(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
        self.url = reverse('device-list')

    def test_get_devices(self):
        DeviceFactory.create_batch(3, owner=self.user)
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_create_device(self):
        location = LocationFactory()
        department = DepartmentFactory()
        data = {
            'name': 'New Device',
            'device_model': 'Model X',
            'repair_price': 100.00,
            'location': location.id,
            'department': department.id,
            'imei': '123456789012345',
            'serial_number': 'SN123456',
        }
        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Device'

    def test_update_device(self):
        device = DeviceFactory(owner=self.user)
        url = reverse('device-detail', args=[device.id])
        data = {'name': 'Updated Device'}
        response = self.client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Updated Device'

    def test_delete_device(self):
        device = DeviceFactory(owner=self.user)
        url = reverse('device-detail', args=[device.id])
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

# /////////////////////////////////////////////////////////////////////////////////////////////
# Test Device Urls
import pytest
from rest_framework import status
from django.urls import reverse
from cart.factories import DeviceFactory, UserFactory

@pytest.mark.django_db
class TestDeviceURLs:

    def setup_method(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)

    def test_device_list_url(self):
        url = reverse('device-list')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_device_detail_url(self):
        device = DeviceFactory(owner=self.user)
        url = reverse('device-detail', args=[device.id])
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
