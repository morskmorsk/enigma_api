# models.py

from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import models

# =============================================================================
# User Profile Model
# =============================================================================

class UserProfile(models.Model):
    """
    Extends the built-in User model to include additional fields:
    - phone_number
    - carrier
    - monthly_payment
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    phone_number = models.CharField(max_length=20, blank=True)
    carrier = models.CharField(max_length=100, blank=True, null=True)
    monthly_payment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.user.username}'s profile"

# =============================================================================
# Location Model
# =============================================================================

class Location(models.Model):
    """
    Represents a physical location where products are stored or sold.
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# =============================================================================
# Department Model
# =============================================================================

class Department(models.Model):
    """
    Categorizes products and devices into departments.
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_taxable = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# =============================================================================
# Product Model
# =============================================================================

class Product(models.Model):
    """
    Represents a product available for sale.
    """
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    barcode = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True
    )
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    on_hand = models.IntegerField(default=0)
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

    def clean(self):
        """
        Validates the image file type and size.
        """
        super().clean()
        if self.image and hasattr(self.image.file, 'size'):
            valid_extensions = ('.jpg', '.jpeg', '.png', '.tiff', '.webp')
            if not self.image.name.lower().endswith(valid_extensions):
                raise ValidationError('Only .jpg, .jpeg, .tiff, .webp, and .png files are allowed.')
            if self.image.file.size > 5 * 1024 * 1024:  # Limit size to 5 MB
                raise ValidationError('The image file size cannot exceed 5 MB.')

    def update_inventory(self, inventory_quantity):
        """
        Updates the inventory quantity of the product.
        """
        self.on_hand = inventory_quantity
        self.save()

# =============================================================================
# Device Model
# =============================================================================

class Device(models.Model):
    """
    Represents a device owned by a user, which can be repaired or serviced.
    """
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    device_model = models.CharField(max_length=255, blank=True, null=True)
    repair_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(
        upload_to='devices/',
        blank=True,
        null=True
    )
    barcode = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True
    )
    imei = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    serial_number = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    defect = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    carrier = models.CharField(max_length=255, blank=True, null=True)
    estimated_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    passcode = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['owner', 'imei'], name='unique_imei_per_owner'),
            models.UniqueConstraint(fields=['owner', 'serial_number'], name='unique_serial_number_per_owner'),
        ]

    def __str__(self):
        return f"{self.name} ({self.device_model}) - Owned by {self.owner.username}"

# =============================================================================
    def clean(self):
        super().clean()
        # Validate image
        if self.image and hasattr(self.image.file, 'size'):
            valid_extensions = ('.jpg', '.jpeg', '.png', '.tiff', '.webp')
            if not self.image.name.lower().endswith(valid_extensions):
                raise ValidationError('Only .jpg, .jpeg, .tiff, .webp, and .png files are allowed.')
            if self.image.file.size > 5 * 1024 * 1024:
                raise ValidationError('The image file size cannot exceed 5 MB.')
        # Validate IMEI uniqueness per owner
        if self.imei and Device.objects.filter(imei=self.imei, owner=self.owner).exclude(pk=self.pk).exists():
            raise ValidationError({'imei': 'Device with this IMEI already exists.'})
        # Validate Serial Number uniqueness per owner
        if self.serial_number and Device.objects.filter(serial_number=self.serial_number, owner=self.owner).exclude(pk=self.pk).exists():
            raise ValidationError({'serial_number': 'Device with this serial number already exists.'})
# =============================================================================
    def save(self, *args, **kwargs):
        """
        Overridden save method to perform full clean before saving.
        """
        self.full_clean()  # Trigger custom validation
        super(Device, self).save(*args, **kwargs)

# =============================================================================
# Cart and CartItem Models
# =============================================================================

class Cart(models.Model):
    """
    Represents a shopping cart associated with a user.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart for {self.user.username}"

    @property
    def total(self):
        """
        Calculates the total price of all items in the cart.
        """
        return sum(item.total_price for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        related_name='items',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    device = models.ForeignKey(
        Device,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
    override_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if not self.product and not self.device:
            raise ValidationError('Either product or device must be set.')
        if self.product and self.device:
            raise ValidationError('Only one of product or device can be set.')

    def __str__(self):
        return f"{self.quantity} x {self.get_item_name()}"

    def get_item_name(self):
        if self.product:
            return self.product.name
        elif self.device:
            return self.device.name
        return 'Unknown Item'

    @property
    def effective_price(self):
        base_price = self.override_price
        if base_price is None:
            if self.product:
                base_price = self.product.price
            elif self.device:
                base_price = self.device.repair_price or Decimal('0.00')
            else:
                base_price = Decimal('0.00')
        return base_price

    @property
    def total_price(self):
        return self.effective_price * self.quantity

# =============================================================================
# Order and OrderItem Models
# =============================================================================

class Order(models.Model):
    """
    Represents an order placed by a user.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order {self.id} - {self.user.username}"

class OrderItem(models.Model):
    """
    Represents an item within an order.
    """
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    device = models.ForeignKey(
        Device,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )  # Price at the time of purchase

    def clean(self):
        super().clean()
        if not self.product and not self.device:
            raise ValidationError('Either product or device must be set.')
        if self.product and self.device:
            raise ValidationError('Only one of product or device can be set.')

    def __str__(self):
        return f"{self.quantity} x {self.get_item_name()} in Order {self.order.id}"

    def get_item_name(self):
        if self.product:
            return self.product.name
        elif self.device:
            return self.device.name
        return 'Unknown Item'
