# models.py
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.conf import settings
from decimal import Decimal

# User profile model for phone number, carrier, and monthly payment
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True)
    carrier = models.CharField(max_length=100, blank=True, null= True)  # New field for carrier
    monthly_payment = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # New field for monthly payment

    def __str__(self):
        return f"{self.user.username}'s profile"

# /////////////////////////////////////////////////////////////////////////////////////////////
# location model
class Location(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

#  department model
class Department(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_taxable = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

#  product model
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/', blank=True)
    barcode = models.CharField(max_length=100, blank=True, null=True, unique=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    on_hand = models.IntegerField(default=0)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def clean(self):
            super().clean()
            # Validate the image file type and size
            if self.image:
                if not self.image.name.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.webp')):
                    raise ValidationError('Only .jpg, .jpeg, .tiff, .webp and .png files are allowed.')
                if self.image.size > 5 * 1024 * 1024:  # Limit size to 5 MB
                    raise ValidationError('The image file size cannot exceed 5 MB.')

    def update_inventory(self, inventory_quantity):
        self.on_hand = inventory_quantity
        self.save()
