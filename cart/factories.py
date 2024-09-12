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