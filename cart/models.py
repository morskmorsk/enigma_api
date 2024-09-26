from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import models
from django.core.validators import FileExtensionValidator
from django_cryptography.fields import encrypt

# =============================================================================
# UserProfile Model
# =============================================================================
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    carrier = models.CharField(max_length=100, blank=True, null=True)
    monthly_payment = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['user__username']

# =============================================================================
# Location Model
# =============================================================================
class Location(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
   
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'
        ordering = ['name']

# =============================================================================
# Department Model
# =============================================================================
class Department(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    is_taxable = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
   
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        ordering = ['name']

# =============================================================================
# Validators for Image Fields
# =============================================================================
def validate_image_size(file):
    max_size = 5 * 1024 * 1024  # 5 MB
    if file.size > max_size:
        raise ValidationError('The image file size cannot exceed 5 MB.')

# =============================================================================
# Product Model
# =============================================================================
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(
        upload_to='products/', blank=True, null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'tiff', 'webp']),
            validate_image_size,
        ]
    )
    barcode = models.CharField(max_length=100, blank=True, null=True, default=None)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    on_hand = models.IntegerField(default=0)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_percentage = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sale_start = models.DateTimeField(null=True, blank=True)
    sale_end = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
   
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['name']

    def update_inventory(self, inventory_quantity):
        self.on_hand = inventory_quantity
        self.save()

# =============================================================================
# Device Model
# =============================================================================
class Device(models.Model):
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    device_model = models.CharField(max_length=255, blank=True, null=True)
    repair_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(
        upload_to='devices/', blank=True, null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'tiff', 'webp']),
            validate_image_size,
        ]
    )
    barcode = models.CharField(max_length=100, blank=True, null=True, default=None)
    imei = models.CharField(max_length=15, blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, blank=True, null=True)
    serial_number = models.CharField(max_length=255, blank=True, null=True)
    defect = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    carrier = models.CharField(max_length=255, blank=True, null=True)
    estimated_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    passcode = encrypt(models.CharField(max_length=50, blank=True, null=True))
    is_available = models.BooleanField(default=True)
    is_repairable = models.BooleanField(default=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_percentage = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sale_start = models.DateTimeField(null=True, blank=True)
    sale_end = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
   
    def __str__(self):
        return f"{self.name} ({self.device_model}) - Owned by {self.owner.user.username}"

    class Meta:
        verbose_name = 'Device'
        verbose_name_plural = 'Devices'
        ordering = ['id']

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Device, self).save(*args, **kwargs)

# =============================================================================
# Cart Model
# =============================================================================
class Cart(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
   
    def __str__(self):
        return f"Cart for {self.user.user.username}"

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
        ordering = ['id']

    @property
    def total(self):
        return sum(item.total_price for item in self.items.all())

# =============================================================================
# CartItem Model
# =============================================================================
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.CASCADE)
    device = models.ForeignKey(Device, null=True, blank=True, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    override_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
   
    def __str__(self):
        return f"{self.quantity} x {self.get_item_name()}"

    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        ordering = ['id']

    def clean(self):
        super().clean()
        if not self.product and not self.device:
            raise ValidationError('Either product or device must be set.')
        if self.product and self.device:
            raise ValidationError('Only one of product or device can be set.')
        if self.quantity <= 0:
            raise ValidationError('Quantity must be greater than zero.')

    def get_item_name(self):
        if self.product:
            return self.product.name
        elif self.device:
            return self.device.name
        return 'Unknown Item'

    @property
    def effective_price(self):
        if self.override_price is not None:
            return self.override_price
        elif self.price is not None:
            return self.price
        elif self.product:
            return self.product.price
        elif self.device and self.device.repair_price is not None:
            return self.device.repair_price
        else:
            raise ValidationError('Price cannot be determined for this item.')

    @property
    def total_price(self):
        return self.effective_price * self.quantity

# =============================================================================
# Order Model
# =============================================================================
class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
   
    def __str__(self):
        return f"Order {self.id} - {self.user.user.username}"

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']

# =============================================================================
# OrderItem Model
# =============================================================================
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.CASCADE)
    device = models.ForeignKey(Device, null=True, blank=True, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
   
    def __str__(self):
        return f"{self.quantity} x {self.get_item_name()} in Order {self.order.id}"

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        ordering = ['order__id']

    def clean(self):
        super().clean()
        if not self.product and not self.device:
            raise ValidationError('Either product or device must be set.')
        if self.product and self.device:
            raise ValidationError('Only one of product or device can be set.')

    def get_item_name(self):
        if self.product:
            return self.product.name
        elif self.device:
            return self.device.name
        return 'Unknown Item'