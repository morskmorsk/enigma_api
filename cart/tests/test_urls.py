from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
import pytest

@pytest.mark.django_db
class TestURLPatterns:

    def setup_method(self):
        self.client = APIClient()

    def test_admin_url(self):
        response = self.client.get('/admin/')
        assert response.status_code == status.HTTP_200_OK or response.status_code == status.HTTP_302_FOUND

    def test_api_urls(self):
        response = self.client.get('/api/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED]

    def test_swagger_ui(self):
        response = self.client.get('/api/schema/swagger-ui/')
        assert response.status_code == status.HTTP_200_OK

    def test_redoc_ui(self):
        response = self.client.get('/api/schema/redoc/')
        assert response.status_code == status.HTTP_200_OK

    def test_invalid_url(self):
        response = self.client.get('/invalid-url/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_media_url(self):
        # Test that media files are being served correctly in DEBUG mode
        if settings.DEBUG:
            media_url = settings.MEDIA_URL + 'test_media_file.jpg'
            response = self.client.get(media_url)
            # If no file exists, assert 404; otherwise, it should return 200
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

# ================================================================================================
# tests/test_urls.py

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse

# =============================================================================
# Tests for URLs
# =============================================================================

@pytest.mark.django_db
class TestURLs:
    """
    Test suite for API endpoints.
    """

    def setup_method(self):
        """
        Initialize the APIClient for the tests.
        """
        self.client = APIClient()

    def test_location_url(self):
        """
        Test that the location list URL returns a 200 OK status.
        """
        url = reverse('location-list')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_department_url(self):
        """
        Test that the department list URL returns a 200 OK status.
        """
        url = reverse('department-list')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_product_url(self):
        """
        Test that the product list URL returns a 200 OK status.
        """
        url = reverse('product-list')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
# ================================================================================================
