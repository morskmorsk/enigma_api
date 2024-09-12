import factory
from django.contrib.auth.models import User
from cart.models import UserProfile

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('user_name')
    email = factory.Faker('email')
    password = factory.PostGenerationMethodCall('set_password', 'password')

class UserProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProfile

    user = factory.SubFactory(UserFactory)
    phone_number = factory.Faker('phone_number')
    carrier = factory.Faker('company')
    monthly_payment = factory.Faker('random_number', digits=5)

# /////////////////////////////////////////////////////////////////////////////////////////////

from django.utils import timezone
from .models import Location, Department, Product


# Location Factory
class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Location

    name = factory.Faker('company')
    description = factory.Faker('paragraph')
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)


# Department Factory
class DepartmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Department

    name = factory.Faker('word')
    description = factory.Faker('paragraph')
    is_taxable = factory.Faker('boolean')
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)


# Product Factory
class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Faker('word')
    price = factory.Faker('pydecimal', left_digits=5, right_digits=2, positive=True)
    description = factory.Faker('paragraph')
    image = factory.django.ImageField(color='blue')
    barcode = factory.Faker('ean13')  # Generates a fake 13-digit barcode
    location = factory.SubFactory(LocationFactory)
    department = factory.SubFactory(DepartmentFactory)
    is_available = factory.Faker('boolean')
    on_hand = factory.Faker('random_int', min=0, max=100)
    cost = factory.Faker('pydecimal', left_digits=5, right_digits=2, positive=True)
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)