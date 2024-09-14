# tests/test_userprofile_models.py

import pytest
from django.contrib.auth.models import User
from cart.models import UserProfile
from cart.factories import UserFactory, UserProfileFactory

# =============================================================================
# Tests for the UserProfile Model
# =============================================================================

@pytest.mark.django_db
class TestUserProfileModel:
    """
    Test suite for the UserProfile model.
    """

    def test_userprofile_creation(self):
        """
        Test the creation of a UserProfile object using the factory.
        Ensures that the UserProfile and associated User are created correctly.
        """
        profile = UserProfileFactory(
            phone_number="555-1234",
            carrier="Test Carrier",
            monthly_payment=50.00
        )

        assert profile.user.username is not None  # User is automatically created
        assert profile.phone_number == "555-1234"
        assert profile.carrier == "Test Carrier"
        assert profile.monthly_payment == 50.00

    def test_userprofile_str_method(self):
        """
        Test the __str__ method of the UserProfile model.
        Ensures that the string representation is as expected.
        """
        profile = UserProfileFactory()
        expected_str = f"{profile.user.username}'s profile"
        assert str(profile) == expected_str

    def test_userprofile_optional_fields(self):
        """
        Test that optional fields are handled correctly when not provided.
        """
        profile = UserProfileFactory(
            phone_number="",
            carrier=None,
            monthly_payment=None
        )
        assert profile.phone_number == ""
        assert profile.carrier is None
        assert profile.monthly_payment is None

    def test_userprofile_update(self):
        """
        Test updating a UserProfile instance.
        Ensures that changes are saved correctly to the database.
        """
        profile = UserProfileFactory()

        # Update fields
        profile.phone_number = "987-654-3210"
        profile.carrier = "New Carrier"
        profile.monthly_payment = 150.00
        profile.save()

        # Retrieve updated profile
        updated_profile = UserProfile.objects.get(pk=profile.pk)
        assert updated_profile.phone_number == "987-654-3210"
        assert updated_profile.carrier == "New Carrier"
        assert updated_profile.monthly_payment == 150.00

    def test_userprofile_delete(self):
        """
        Test that a UserProfile can be deleted independently.
        """
        profile = UserProfileFactory()
        user = profile.user

        profile.delete()
        assert not UserProfile.objects.filter(pk=profile.pk).exists()
        assert UserProfile.objects.filter(user=user).count() == 0
        # The associated User should still exist
        assert User.objects.filter(pk=user.pk).exists()

    def test_userprofile_one_to_one_relationship(self):
        """
        Test the one-to-one relationship between User and UserProfile.
        Ensures that the User has a related UserProfile.
        """
        profile = UserProfileFactory()
        user = profile.user

        # Access the profile via the user
        assert user.profile == profile  # Requires related_name='profile' in the UserProfile model

    def test_deleting_user_deletes_profile(self):
        """
        Test that deleting a User also deletes the associated UserProfile.
        """
        profile = UserProfileFactory()
        user = profile.user

        user.delete()

        with pytest.raises(UserProfile.DoesNotExist):
            UserProfile.objects.get(pk=profile.pk)
        # Ensure the User is also deleted
        assert not User.objects.filter(pk=user.pk).exists()