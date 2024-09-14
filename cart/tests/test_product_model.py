# =============================================================================
# Tests for the Product Model
# =============================================================================
from io import BytesIO
import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from cart.factories import LocationFactory, DepartmentFactory, ProductFactory
from PIL import Image

@pytest.mark.django_db
class TestProductModel:
    """
    Test suite for the Product model.
    """

    def test_product_str(self):
        """
        Test the string representation of a Product instance.
        """
        product = ProductFactory(name="Smartphone")
        assert str(product) == "Smartphone"

    def test_product_inventory_update(self):
        """
        Test the 'update_inventory' method of the Product model.
        """
        product = ProductFactory(name="Laptop", on_hand=10)
        product.update_inventory(20)
        assert product.on_hand == 20
# =============================================================================

    def test_product_clean(self):
        """
        Test the image validation in the Product model's clean method.
        """
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
        product = ProductFactory(image=valid_image)
        try:
            product.full_clean()  # Should pass without errors
        except ValidationError as e:
            pytest.fail(f"ValidationError raised unexpectedly for a valid image: {e}")

        # Test with an invalid image file extension (should fail)
        invalid_image = SimpleUploadedFile(
            "invalid_file.txt",
            b"file_content",
            content_type="text/plain"
        )
        product.image = invalid_image
        with pytest.raises(ValidationError) as excinfo:
            product.full_clean()
        expected_error = "Only .jpg, .jpeg, .tiff, .webp, and .png files are allowed."
        assert expected_error in str(excinfo.value)

# ================================================================================================
