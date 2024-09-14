# tests/test_device_model.py

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from cart.factories import DeviceFactory
from PIL import Image
from io import BytesIO

# =============================================================================
# Tests for the Device Model
# =============================================================================

@pytest.mark.django_db
class TestDeviceModel:
    """
    Test suite for the Device model.
    """
# =============================================================================

    def test_device_str(self):
        """
        Test the string representation of the Device model.
        """
        device = DeviceFactory(name="iPhone", device_model="13 Pro")
        expected_str = f"iPhone (13 Pro) - Owned by {device.owner.username}"
        assert str(device) == expected_str

# =============================================================================

    def test_device_image_validation(self):
        """
        Test the image validation in the Device model's full_clean method.
        """
# =============================================================================
        # === Test with a valid image (should pass) ===
        # Create a valid image in memory
        image_io = BytesIO()
        image = Image.new('RGB', (100, 100), 'blue')
        image.save(image_io, format='JPEG')
        image_io.seek(0)
        valid_image = SimpleUploadedFile(
            "valid_image.jpg",
            image_io.read(),
            content_type="image/jpeg"
        )
        device = DeviceFactory(image=valid_image)
        try:
            device.full_clean()  # Should pass without errors
        except ValidationError as e:
            pytest.fail(f"ValidationError raised unexpectedly for a valid image: {e}")
# =====================================================================================

        # === Test with an invalid image file extension (should fail) ===
        invalid_image = SimpleUploadedFile(
            "invalid_file.txt",
            b"file_content",
            content_type="text/plain"
        )
        device.image = invalid_image
        with pytest.raises(ValidationError) as excinfo:
            device.full_clean()
        expected_error = "Only .jpg, .jpeg, .tiff, .webp, and .png files are allowed."
        assert expected_error in str(excinfo.value)

# ================================================================================================
        # === Test with an image that exceeds the size limit (should fail) ===
        # Create a large image that exceeds 5 MB
        large_image_io = BytesIO()
        # Increase dimensions significantly to create a large image
        large_image = Image.new('RGB', (8000, 8000), 'blue')
        # Save the image as PNG with minimal compression
        large_image.save(large_image_io, format='PNG', optimize=False, compress_level=0)
        large_image_io.seek(0)
        # Check the size of the image
        image_size = large_image_io.getbuffer().nbytes
        assert image_size > 5 * 1024 * 1024, f"Test image size is not larger than 5 MB, actual size: {image_size} bytes"
        large_image_file = SimpleUploadedFile(
            "large_image.png",
            large_image_io.read(),
            content_type="image/png"
        )
        device.image = large_image_file
        with pytest.raises(ValidationError) as excinfo:
            device.full_clean()
        assert "The image file size cannot exceed 5 MB." in str(excinfo.value)

# =============================================================================

    def test_imei_uniqueness(self):
        """
        Test the uniqueness constraint on the 'imei' field.
        """
        # Create the first device with a unique IMEI
        device1 = DeviceFactory(imei="123456789012345")

        # Build the second device with the same IMEI and same owner
        device2 = DeviceFactory.build(imei="123456789012345", owner=device1.owner)
        with pytest.raises(ValidationError) as excinfo:
            device2.full_clean()  # Triggers validation
        errors = excinfo.value.message_dict
        assert 'imei' in errors
        expected_error = "Device with this IMEI already exists."
        actual_error = errors['imei'][0]
        assert actual_error == expected_error, f"Expected '{expected_error}', got '{actual_error}'"

# =============================================================================

    def test_serial_number_uniqueness(self):
        """
        Test the uniqueness constraint on the 'serial_number' field.
        """
        # Create the first device with a unique serial number
        device1 = DeviceFactory(serial_number="SN123456")

        # Build the second device with the same serial number and same owner
        device2 = DeviceFactory.build(serial_number="SN123456", owner=device1.owner)
        with pytest.raises(ValidationError) as excinfo:
            device2.full_clean()  # Triggers validation
        errors = excinfo.value.message_dict
        assert 'serial_number' in errors
        expected_error = "Device with this serial number already exists."
        actual_error = errors['serial_number'][0]
        assert actual_error == expected_error, f"Expected '{expected_error}', got '{actual_error}'"
        