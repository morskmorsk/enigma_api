# =============================================================================
# Tests for the Department Model
# =============================================================================
import pytest
from cart.factories import DepartmentFactory

@pytest.mark.django_db
class TestDepartmentModel:
    """
    Test suite for the Department model.
    """

    def test_department_str(self):
        """
        Test the string representation of a Department instance.
        """
        department = DepartmentFactory(name="Electronics")
        assert str(department) == "Electronics"

    def test_department_is_taxable(self):
        """
        Test the 'is_taxable' field of the Department model.
        """
        department = DepartmentFactory(name="Grocery", is_taxable=False)
        assert not department.is_taxable

