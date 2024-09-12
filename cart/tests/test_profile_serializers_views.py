
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from cart.serializers import UserProfileSerializer
from cart.models import UserProfile
from cart.factories import UserFactory, UserProfileFactory


# Serializer Tests
@pytest.mark.django_db
class TestUserProfileSerializer:

    def setup_method(self):
        self.user_data = {
            'username': 'testuser',
            'password': 'testpass123',
            'email': 'testuser@example.com',
            'phone_number': '+14155552671',
            'carrier': 'Carrier X',
            'monthly_payment': 50
        }

    def test_valid_data(self):
        # Test that valid data passes validation
        serializer = UserProfileSerializer(data=self.user_data)
        assert serializer.is_valid(), serializer.errors

    def test_missing_username(self):
        # Test that missing username raises validation errors
        invalid_data = self.user_data.copy()
        invalid_data.pop('username')
        serializer = UserProfileSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert 'username' in serializer.errors

    def test_invalid_email(self):
        # Test that invalid email raises validation errors
        invalid_data = self.user_data.copy()
        invalid_data['email'] = 'invalid_email'
        serializer = UserProfileSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    def test_optional_email(self):
        # Test that email is optional
        valid_data = self.user_data.copy()
        valid_data.pop('email')
        serializer = UserProfileSerializer(data=valid_data)
        assert serializer.is_valid(), serializer.errors


# View Tests
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from cart.factories import UserFactory, UserProfileFactory

@pytest.mark.django_db
class TestUserProfileViewSet:

    def setup_method(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.user_profile = UserProfileFactory(user=self.user)
        self.client.force_authenticate(user=self.user)
        self.url = reverse('profile-list')  # This sets the correct URL to use in tests

    def test_get_user_profiles(self):
        # Use the already authenticated client and URL
        response = self.client.get(self.url)
        assert response.status_code == 200

    def test_create_user_profile(self):
        data = {
            'username': 'newuser',
            'password': 'newpassword',
            'email': 'newuser@example.com',
        }
        response = self.client.post(self.url, data, format='json')
        assert response.status_code == 201

    def test_unauthenticated_access(self):
        # Clear authentication to test unauthenticated access
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        assert response.status_code == 403  # Unauthenticated users should be denied access