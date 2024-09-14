# =============================================================================
# Tests for the Department Serializer
# =============================================================================
import pytest
from cart.serializers import DepartmentSerializer
from cart.factories import DepartmentFactory

@pytest.mark.django_db
class TestDepartmentSerializer:
    """
    Test suite for the DepartmentSerializer.
    """

    def test_valid_department_serializer(self):
        """
        Test that the DepartmentSerializer serializes data correctly for a valid instance.
        """
        department = DepartmentFactory()
        serializer = DepartmentSerializer(instance=department)
        assert serializer.data['name'] == department.name

    def test_invalid_department_serializer(self):
        """
        Test that the DepartmentSerializer handles invalid data correctly.
        """
        invalid_data = {'name': ''}
        serializer = DepartmentSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert 'name' in serializer.errors