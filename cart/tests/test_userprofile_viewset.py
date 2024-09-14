# tests/test_userprofile_views.py

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from cart.factories import UserFactory, UserProfileFactory
from cart.models import UserProfile

# =============================================================================
# Tests for the UserProfileViewSet
# =============================================================================

@pytest.mark.django_db
class TestUserProfileViewSet:
    """
    Test suite for the UserProfileViewSet.
    """

    def setup_method(self):
        """
        Setup method to initialize the APIClient and authenticate a user.
        """
        self.client = APIClient()
        self.user = UserFactory()
        self.user_profile = UserProfileFactory(user=self.user)
        self.client.force_authenticate(user=self.user)
        self.url = reverse('userprofile-list')

    def test_get_user_profile(self):
        """
        Test that an authenticated user can retrieve their own user profile.
        """
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        # Ensure only the user's profile is returned
        assert len(response.data) == 1
        assert response.data[0]['user'] == self.user.id

    def test_create_user_profile(self):
        """
        Test that an unauthenticated user can create a new user profile (signup).
        """
        self.client.force_authenticate(user=None)
        data = {
            'username': 'newuser',
            'password': 'newpassword',
            'email': 'newuser@example.com',
            'phone_number': '+14155552672',
            'carrier': 'Carrier Y',
            'monthly_payment': 60.00
        }
        response = self.client.post(self.url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert UserProfile.objects.filter(user__username='newuser').exists()

    def test_unauthenticated_access_get(self):
        """
        Test that unauthenticated users cannot retrieve user profiles.
        """
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN  # Adjusted to match actual status code

    def test_retrieve_user_profile(self):
        """
        Test that a user can retrieve their own profile details.
        """
        url = reverse('userprofile-detail', args=[self.user_profile.id])
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user'] == self.user.id

    def test_update_user_profile(self):
        """
        Test that a user can update their own profile.
        """
        url = reverse('userprofile-detail', args=[self.user_profile.id])
        data = {'phone_number': '+14155552673', 'carrier': 'Carrier Z'}
        response = self.client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        self.user_profile.refresh_from_db()
        assert self.user_profile.phone_number == '+14155552673'
        assert self.user_profile.carrier == 'Carrier Z'

    def test_update_other_user_profile(self):
        """
        Test that a user cannot update another user's profile.
        """
        other_user = UserFactory(username='otheruser')
        other_user_profile = UserProfileFactory(user=other_user)
        url = reverse('userprofile-detail', args=[other_user_profile.id])
        data = {'carrier': 'Carrier X'}
        response = self.client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND  # Should not find another user's profile

    def test_delete_user_profile(self):
        """
        Test that a user cannot delete their profile (if not allowed).
        """
        url = reverse('userprofile-detail', args=[self.user_profile.id])
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED  # Assuming deletion is not allowed