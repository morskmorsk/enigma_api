# =============================================================================
# Tests for the Location Model
# =============================================================================
import pytest
from cart.factories import LocationFactory

@pytest.mark.django_db
class TestLocationModel:
    """
    Test suite for the Location model.
    """

    def test_location_str(self):
        """
        Test the string representation of a Location instance.
        """
        location = LocationFactory(name="Main Warehouse")
        assert str(location) == "Main Warehouse"

    def test_location_create(self):
        """
        Test that a Location instance is created with the correct name.
        """
        location = LocationFactory(name="Secondary Warehouse")
        assert location.name == "Secondary Warehouse"

