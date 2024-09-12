
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
@pytest.mark.django_db
class TestUserProfileViewSet:

    def setup_method(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.user_profile = UserProfileFactory(user=self.user)
        self.client.force_authenticate(user=self.user)
        self.url = reverse('userprofile-list')

    def test_get_user_profiles(self):
        # Test fetching user profiles with authentication
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

    def test_create_user_profile(self):
        # Test creating a new user profile
        data = {
            'username': 'newuser',
            'password': 'newpassword123',
            'email': 'newuser@example.com',
            'phone_number': '+14155552672',
            'carrier': 'Carrier Y',
            'monthly_payment': 75
        }
        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_unauthenticated_access(self):
        # Test that unauthenticated access is denied
        self.client.logout()  # Log out the authenticated user
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

