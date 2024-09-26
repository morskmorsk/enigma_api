import factory
from decimal import Decimal
from django.contrib.auth.models import User
from django.utils import timezone
from .models import (
    UserProfile,
    Location,
    Department,
    Product,
    Device,
    Cart,
    CartItem,
    Order,
    OrderItem
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

    # Set and save the password
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

class DepartmentFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating Department instances.
    """
    class Meta:
        model = Department

    name = factory.Faker('word')
    description = factory.Faker('paragraph')
    is_taxable = factory.Faker('boolean')

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
    barcode = factory.Faker('ean13')
    location = factory.SubFactory(LocationFactory)
    department = factory.SubFactory(DepartmentFactory)
    is_available = factory.Faker('boolean')
    on_hand = factory.Faker('random_int', min=0, max=100)
    cost = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)

class DeviceFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating Device instances.
    """
    class Meta:
        model = Device

    name = factory.Faker('word')
    owner = factory.SubFactory(UserProfileFactory)
    device_model = factory.Faker('word')
    repair_price = factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=True)
    description = factory.Faker('paragraph')
    image = factory.django.ImageField(color='red')
    barcode = factory.Faker('ean13')
    imei = factory.Faker('numerify', text='###############')  # 15-digit IMEI
    serial_number = factory.Faker('ean13')
    location = factory.SubFactory(LocationFactory)
    department = factory.SubFactory(DepartmentFactory)
    defect = factory.Faker('paragraph')
    notes = factory.Faker('paragraph')
    carrier = factory.Faker('company')
    estimated_value = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    passcode = factory.Faker('password')

# =============================================================================
# Cart and CartItem Factories
# =============================================================================

class CartFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating Cart instances.
    """
    class Meta:
        model = Cart

    user = factory.SubFactory(UserProfileFactory)

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

class CartItemWithProductFactory(CartItemFactory):
    """
    Factory for creating CartItem instances associated with a Product.
    """
    class Meta:
        model = CartItem

    product = factory.SubFactory(ProductFactory)
    device = None  # Ensure device is None
    price = factory.LazyAttribute(lambda obj: obj.product.price)

class CartItemWithDeviceFactory(CartItemFactory):
    """
    Factory for creating CartItem instances associated with a Device.
    """
    class Meta:
        model = CartItem

    device = factory.SubFactory(DeviceFactory)
    product = None  # Ensure product is None
    price = factory.LazyAttribute(lambda obj: obj.device.repair_price or Decimal('0.00'))

# =============================================================================
# Order and OrderItem Factories
# =============================================================================

class OrderFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating Order instances.
    """
    class Meta:
        model = Order

    user = factory.SubFactory(UserProfileFactory)
    status = 'pending'
    total = Decimal('0.00')

class OrderItemFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating OrderItem instances.
    """
    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
    product = factory.SubFactory(ProductFactory)
    device = None
    quantity = factory.Faker('random_int', min=1, max=5)
    price = factory.LazyAttribute(lambda obj: obj.product.price)