# factories.py

import factory
from django.contrib.auth.models import User
from django.utils import timezone

from cart.models import (
    UserProfile,
    Location,
    Department,
    Product,
    Device,
    Cart,
    CartItem
)

# =============================================================================
# User and UserProfile Factories
# =============================================================================

class UserFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating User instances.
    """
    class Meta:
        model = User
        django_get_or_create = ('username',)

    username = factory.Faker('user_name')
    email = factory.Faker('email')

    # Password needs to be set using set_password to hash it correctly
    password = factory.PostGenerationMethodCall('set_password', 'password')


class UserProfileFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating UserProfile instances.
    """
    class Meta:
        model = UserProfile

    user = factory.SubFactory(UserFactory)
    phone_number = factory.Faker('phone_number')
    carrier = factory.Faker('company')
    monthly_payment = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)

# =============================================================================
# Location and Department Factories
# =============================================================================

class LocationFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating Location instances.
    """
    class Meta:
        model = Location

    name = factory.Faker('company')
    description = factory.Faker('paragraph')
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)


class DepartmentFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating Department instances.
    """
    class Meta:
        model = Department

    name = factory.Faker('word')
    description = factory.Faker('paragraph')
    is_taxable = factory.Faker('boolean')
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)

# =============================================================================
# Product and Device Factories
# =============================================================================

class ProductFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating Product instances.
    """
    class Meta:
        model = Product

    name = factory.Faker('word')
    price = factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=True)
    description = factory.Faker('paragraph')
    image = factory.django.ImageField(color='blue')
    barcode = factory.Faker('ean13')  # Generates a fake 13-digit barcode
    location = factory.SubFactory(LocationFactory)
    department = factory.SubFactory(DepartmentFactory)
    is_available = factory.Faker('boolean')
    on_hand = factory.Faker('random_int', min=0, max=100)
    cost = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)


class DeviceFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating Device instances.
    """
    class Meta:
        model = Device

    name = factory.Faker('word')
    owner = factory.SubFactory(UserFactory)
    device_model = factory.Faker('word')
    repair_price = factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=True)
    description = factory.Faker('paragraph')
    image = factory.django.ImageField(color='red')
    barcode = factory.Faker('ean13')
    imei = factory.Faker('numerify', text='###############')  # Generates a 15-digit IMEI
    serial_number = factory.Faker('ean13')
    location = factory.SubFactory(LocationFactory)
    department = factory.SubFactory(DepartmentFactory)
    defect = factory.Faker('paragraph')
    notes = factory.Faker('paragraph')
    carrier = factory.Faker('company')
    estimated_value = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    passcode = factory.Faker('password')
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)

# =============================================================================
# Cart and CartItem Factories
# =============================================================================

class CartFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating Cart instances.
    """
    class Meta:
        model = Cart

    user = factory.SubFactory(UserFactory)
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)


class CartItemFactory(factory.django.DjangoModelFactory):
    """
    Base factory for creating CartItem instances.
    Note: This is an abstract factory; use CartItemWithProductFactory or
    CartItemWithDeviceFactory to create instances.
    """
    class Meta:
        model = CartItem
        abstract = True

    cart = factory.SubFactory(CartFactory)
    quantity = factory.Faker('random_int', min=1, max=5)
    override_price = None
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)


class CartItemWithProductFactory(CartItemFactory):
    """
    Factory for creating CartItem instances associated with a Product.
    """
    class Meta:
        model = CartItem

    product = factory.SubFactory(ProductFactory)
    device = None  # Ensure device is None


class CartItemWithDeviceFactory(CartItemFactory):
    """
    Factory for creating CartItem instances associated with a Device.
    """
    class Meta:
        model = CartItem

    device = factory.SubFactory(DeviceFactory)
    product = None  # Ensure product is None