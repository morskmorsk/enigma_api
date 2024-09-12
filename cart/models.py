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


class Device(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    name = models.CharField(max_length=255)
    device_model = models.CharField(max_length=255, blank=True, null=True)
    repair_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='devices/', blank=True, null=True)
    barcode = models.CharField(max_length=100, blank=True, null=True, unique=True)
    imei = models.CharField(max_length=15, unique=True, blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, blank=True, null=True)
    serial_number = models.CharField(max_length=255, unique=True, blank=True, null=True)
    defect = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    carrier = models.CharField(max_length=255, blank=True, null=True)
    estimated_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    passcode = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.device_model}) - Owned by {self.owner.username}"

    def clean(self):
            super().clean()
            if self.image:
                if not self.image.name.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.webp')):
                    raise ValidationError('Only .jpg, .jpeg, .tiff, .webp and .png files are allowed.')
                if self.image.size > 5 * 1024 * 1024:
                    raise ValidationError('The image file size cannot exceed 5 MB.')
            """
            Custom validation to ensure uniqueness of 'imei' and 'serial_number' 
            only when they are provided.
            """
            if self.imei:
                if Device.objects.filter(imei=self.imei).exclude(id=self.id).exists():
                    raise ValidationError("A device with this IMEI already exists.")

            if self.serial_number:
                if Device.objects.filter(serial_number=self.serial_number).exclude(id=self.id).exists():
                    raise ValidationError("A device with this serial number already exists.")
            

    def save(self, *args, **kwargs):
        self.full_clean()  # Call full_clean to trigger custom validation
        super(Device, self).save(*args, **kwargs)


# /////////////////////////////////////////////////////////////////////////////////////////////
# Cart and CartItem models
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    @property
    def total(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)

    # Generic ForeignKey to allow Product or Device
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    quantity = models.PositiveIntegerField(default=1)
    override_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    effective_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.quantity} x {self.content_object}"

    @property
    def effective_price(self):
        if hasattr(self.content_object, 'price'):
            return self.override_price if self.override_price is not None else self.content_object.price
        elif hasattr(self.content_object, 'repair_price'):
            return self.override_price if self.override_price is not None else self.content_object.repair_price
        return Decimal('0.00')

    @property
    def total_price(self):
        return self.effective_price * self.quantity
    