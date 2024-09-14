# tests/test_userprofile_serializers.py

import pytest
from rest_framework import serializers
from django.contrib.auth.models import User
from cart.models import UserProfile
from cart.serializers import UserProfileSerializer
from cart.factories import UserFactory, UserProfileFactory

# =============================================================================
# Tests for the UserProfileSerializer
# =============================================================================

@pytest.mark.django_db
class TestUserProfileSerializer:
    """
    Test suite for the UserProfileSerializer.
    """

    def setup_method(self):
        """
        Setup method to initialize valid user data for tests.
        """
        self.user_data = {
            'username': 'testuser',
            'password': 'testpass123',
            'email': 'testuser@example.com',
            'phone_number': '+14155552671',
            'carrier': 'Carrier X',
            'monthly_payment': 50.00
        }

    def test_valid_data(self):
        """
        Test that valid data passes validation.
        """
        serializer = UserProfileSerializer(data=self.user_data)
        assert serializer.is_valid(), serializer.errors
        user_profile = serializer.save()
        assert user_profile.user.username == self.user_data['username']
        assert user_profile.phone_number == self.user_data['phone_number']

    def test_missing_username(self):
        """
        Test that missing username raises validation errors.
        """
        invalid_data = self.user_data.copy()
        invalid_data.pop('username')
        serializer = UserProfileSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert 'username' in serializer.errors

    def test_invalid_email(self):
        """
        Test that invalid email raises validation errors.
        """
        invalid_data = self.user_data.copy()
        invalid_data['email'] = 'invalid_email'
        serializer = UserProfileSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    def test_optional_email(self):
        """
        Test that email is optional.
        """
        valid_data = self.user_data.copy()
        valid_data.pop('email')
        serializer = UserProfileSerializer(data=valid_data)
        assert serializer.is_valid(), serializer.errors
        user_profile = serializer.save()
        assert user_profile.user.email == ''  # Email should be empty string if not provided

    def test_duplicate_username(self):
        """
        Test that creating a user with an existing username raises validation errors.
        """
        # Create an existing user
        existing_user = UserFactory(username='testuser')
        invalid_data = self.user_data.copy()
        serializer = UserProfileSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert 'username' in serializer.errors
        expected_error = 'A user with that username already exists.'
        actual_error = str(serializer.errors['username'][0])
        assert actual_error == expected_error

    def test_invalid_monthly_payment(self):
        """
        Test that invalid monthly_payment raises validation errors.
        """
        invalid_data = self.user_data.copy()
        invalid_data['monthly_payment'] = -10.00  # Negative value
        serializer = UserProfileSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert 'monthly_payment' in serializer.errors
        expected_error = 'Monthly payment must be a positive value.'
        actual_error = str(serializer.errors['monthly_payment'][0])
        assert actual_error == expected_error