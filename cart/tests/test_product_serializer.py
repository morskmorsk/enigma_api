# =============================================================================
# Tests for the Product Serializer
# =============================================================================
import pytest
from cart.serializers import  ProductSerializer
from cart.factories import LocationFactory, DepartmentFactory, ProductFactory

@pytest.mark.django_db
class TestProductSerializer:
    """
    Test suite for the ProductSerializer.
    """

    def test_valid_product_serializer(self):
        """
        Test that the ProductSerializer serializes data correctly for a valid instance.
        """
        product = ProductFactory()
        serializer = ProductSerializer(instance=product)
        assert serializer.data['name'] == product.name

    def test_invalid_product_serializer(self):
        """
        Test that the ProductSerializer handles invalid data correctly.
        """
        # Create valid location and department first
        location = LocationFactory()
        department = DepartmentFactory()

        # Test invalid 'name' field
        invalid_data_name = {
            'name': '',  # Invalid name
            'price': '100.00',
            'location': location.id,
            'department': department.id
        }
        serializer = ProductSerializer(data=invalid_data_name)
        assert not serializer.is_valid()
        assert 'name' in serializer.errors

        # Test invalid 'price' field
        invalid_data_price = {
            'name': 'Product',  # Valid name
            'price': '-100.00',  # Invalid price (negative)
            'location': location.id,
            'department': department.id
        }
        serializer = ProductSerializer(data=invalid_data_price)
        assert not serializer.is_valid()
        assert 'price' in serializer.errors
# ================================================================================================
