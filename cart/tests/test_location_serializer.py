# =============================================================================
# Tests for the Location Serializer
# =============================================================================
import pytest
from cart.serializers import LocationSerializer, DepartmentSerializer, ProductSerializer
from cart.factories import LocationFactory, DepartmentFactory, ProductFactory

@pytest.mark.django_db
class TestLocationSerializer:
    """
    Test suite for the LocationSerializer.
    """

    def test_valid_location_serializer(self):
        """
        Test that the LocationSerializer serializes data correctly for a valid instance.
        """
        location = LocationFactory()
        serializer = LocationSerializer(instance=location)
        assert serializer.data['name'] == location.name

    def test_invalid_location_serializer(self):
        """
        Test that the LocationSerializer handles invalid data correctly.
        """
        invalid_data = {'name': ''}
        serializer = LocationSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert 'name' in serializer.errors
