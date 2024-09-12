import pytest
from cart.models import UserProfile
from cart.factories import UserFactory, UserProfileFactory

# Mark these tests as requiring database access
pytestmark = pytest.mark.django_db

# tests for the UserProfile model /////////////////////////////////////////////////////////////

def test_userprofile_creation():
    """Test the creation of a UserProfile object using the factory"""
    profile = UserProfileFactory(
        phone_number="555-1234",
        carrier="Test Carrier",
        monthly_payment=50.00
    )

    assert profile.user.username is not None  # User is automatically created with a username
    assert profile.phone_number == "555-1234"
    assert profile.carrier == "Test Carrier"
    assert profile.monthly_payment == 50.00


def test_userprofile_str_method():
    """Test the __str__ method of UserProfile model"""
    profile = UserProfileFactory()
    assert str(profile) == f"{profile.user.username}'s profile"


def test_userprofile_with_optional_fields():
    """Test that optional fields are handled correctly when not provided"""
    profile = UserProfileFactory(phone_number="", carrier=None, monthly_payment=None)
    assert profile.phone_number == ""
    assert profile.carrier is None
    assert profile.monthly_payment is None


def test_userprofile_update():
    """Test updating a UserProfile"""
    profile = UserProfileFactory()

    profile.phone_number = "987-654-3210"
    profile.carrier = "New Carrier"
    profile.monthly_payment = 150.00
    profile.save()

    updated_profile = UserProfile.objects.get(user=profile.user)
    assert updated_profile.phone_number == "987-654-3210"
    assert updated_profile.carrier == "New Carrier"
    assert updated_profile.monthly_payment == 150.00


def test_userprofile_delete():
    """Test that a UserProfile can be deleted"""
    profile = UserProfileFactory()
    profile.delete()
    assert UserProfile.objects.filter(user=profile.user).count() == 0


def test_user_profile_one_to_one():
    """Test the one-to-one relationship between User and UserProfile"""
    profile = UserProfileFactory()
    
    assert profile.user.profile == profile  # Ensure the one-to-one relationship is intact


def test_user_deletes_profile():
    """Test that deleting a User also deletes the associated UserProfile"""
    profile = UserProfileFactory()
    user = profile.user
    user.delete()

    with pytest.raises(UserProfile.DoesNotExist):
        UserProfile.objects.get(user=user)
