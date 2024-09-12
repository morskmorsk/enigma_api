import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from cart.serializers import LocationSerializer, DepartmentSerializer, ProductSerializer
from cart.factories import LocationFactory, DepartmentFactory, ProductFactory


# ----------- Model Tests -----------
@pytest.mark.django_db
class TestLocationModel:

    def test_location_str(self):
        location = LocationFactory(name="Main Warehouse")
        assert str(location) == "Main Warehouse"

    def test_location_create(self):
        location = LocationFactory(name="Secondary Warehouse")
        assert location.name == "Secondary Warehouse"


@pytest.mark.django_db
class TestDepartmentModel:

    def test_department_str(self):
        department = DepartmentFactory(name="Electronics")
        assert str(department) == "Electronics"

    def test_department_is_taxable(self):
        department = DepartmentFactory(name="Grocery", is_taxable=False)
        assert not department.is_taxable


@pytest.mark.django_db
class TestProductModel:

    def test_product_str(self):
        product = ProductFactory(name="Smartphone")
        assert str(product) == "Smartphone"

    def test_product_inventory_update(self):
        product = ProductFactory(name="Laptop", on_hand=10)
        product.update_inventory(20)
        assert product.on_hand == 20

    def test_product_clean(self):
        product = ProductFactory(image=None)
        product.clean()  # This should not raise ValidationError as no image is attached

        with pytest.raises(Exception):
            # Test invalid image extension (assuming a fixture or mock image)
            product.image.name = "invalid_file.txt"
            product.clean()


# ----------- Serializer Tests -----------
@pytest.mark.django_db
class TestLocationSerializer:

    def test_valid_location_serializer(self):
        location = LocationFactory()
        serializer = LocationSerializer(instance=location)
        assert serializer.data['name'] == location.name

    def test_invalid_location_serializer(self):
        invalid_data = {'name': ''}
        serializer = LocationSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert 'name' in serializer.errors


@pytest.mark.django_db
class TestDepartmentSerializer:

    def test_valid_department_serializer(self):
        department = DepartmentFactory()
        serializer = DepartmentSerializer(instance=department)
        assert serializer.data['name'] == department.name

    def test_invalid_department_serializer(self):
        invalid_data = {'name': ''}
        serializer = DepartmentSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert 'name' in serializer.errors


@pytest.mark.django_db
class TestProductSerializer:

    def test_invalid_product_serializer(self):
        # Create valid location and department first
        location = LocationFactory()
        department = DepartmentFactory()

        # Test invalid 'name' field but valid 'price', 'location', and 'department'
        invalid_data_name = {
            'name': '',  # Invalid name
            'price': 100,
            'location': location.id,
            'department': department.id
        }
        serializer = ProductSerializer(data=invalid_data_name)
        assert not serializer.is_valid()
        assert 'name' in serializer.errors

        # Test invalid 'price' field but valid 'name', 'location', and 'department'
        invalid_data_price = {
            'name': 'Product',  # Valid name
            'price': -100,  # Invalid price
            'location': location.id,
            'department': department.id
        }
        serializer = ProductSerializer(data=invalid_data_price)
        assert not serializer.is_valid()
        assert 'price' in serializer.errors

# ----------- View Tests -----------
@pytest.mark.django_db
class TestLocationViewSet:

    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('location-list')

    def test_get_locations(self):
        LocationFactory.create_batch(5)
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 5

    def test_create_location(self):
        data = {'name': 'New Location', 'description': 'A new storage location'}
        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Location'

    def test_invalid_create_location(self):
        data = {'name': ''}
        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestDepartmentViewSet:

    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('department-list')

    def test_get_departments(self):
        DepartmentFactory.create_batch(3)
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_create_department(self):
        data = {'name': 'IT Department', 'description': 'Handles tech stuff', 'is_taxable': True}
        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'IT Department'

    def test_invalid_create_department(self):
        data = {'name': ''}
        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestProductViewSet:

    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('product-list')

    def test_get_products(self):
        ProductFactory.create_batch(2)
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_create_product(self):
        location = LocationFactory()
        department = DepartmentFactory()  # Ensure this is created

        data = {
            'name': 'New Product',
            'price': 499.99,
            'description': 'This is a great product',
            'location': location.id,
            'department': department.id,  # Pass the department id correctly
            'is_available': True
        }

        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Product'

    def test_invalid_create_product(self):
        data = {'name': '', 'price': -100}
        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ----------- URL Tests -----------
@pytest.mark.django_db
class TestURLs:

    def setup_method(self):
        self.client = APIClient()

    def test_location_url(self):
        url = reverse('location-list')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_department_url(self):
        url = reverse('department-list')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_product_url(self):
        url = reverse('product-list')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK