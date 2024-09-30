from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import models
from django.core.validators import FileExtensionValidator
from django_cryptography.fields import encrypt

# =============================================================================
# Sales Tax Rate
# =============================================================================
SALES_TAX_RATE = getattr(settings, 'SALES_TAX_RATE', Decimal('0.07'))  # Default to 7% sales tax

# =============================================================================
# UserProfile Model
# =============================================================================
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True, null=True, default='1234567890')
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
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
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

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Product, self).save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.discount_amount and self.discount_percentage:
            raise ValidationError('Only one of discount_amount or discount_percentage can be set.')
        if self.price < 0:
            raise ValidationError('Price cannot be negative.')
        if self.cost and self.cost < 0:
            raise ValidationError('Cost cannot be negative.')
        if self.discount_amount and self.discount_amount < 0:
            raise ValidationError('Discount amount cannot be negative.')
        if self.discount_percentage and (self.discount_percentage < 0 or self.discount_percentage > 100):
            raise ValidationError('Discount percentage must be between 0 and 100.')

    @property
    def discounted_price(self):
        price = self.price
        if self.discount_amount:
            price -= self.discount_amount
        elif self.discount_percentage:
            price -= price * (self.discount_percentage / Decimal('100'))
        return max(price, Decimal('0.00'))

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
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
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

    def clean(self):
        super().clean()
        if self.discount_amount and self.discount_percentage:
            raise ValidationError('Only one of discount_amount or discount_percentage can be set.')
        if self.repair_price and self.repair_price < 0:
            raise ValidationError('Repair price cannot be negative.')
        if self.estimated_value and self.estimated_value < 0:
            raise ValidationError('Estimated value cannot be negative.')
        if self.discount_amount and self.discount_amount < 0:
            raise ValidationError('Discount amount cannot be negative.')
        if self.discount_percentage and (self.discount_percentage < 0 or self.discount_percentage > 100):
            raise ValidationError('Discount percentage must be between 0 and 100.')

    @property
    def discounted_repair_price(self):
        repair_price = self.repair_price or Decimal('0.00')
        if self.discount_amount:
            repair_price -= self.discount_amount
        elif self.discount_percentage:
            repair_price -= repair_price * (self.discount_percentage / Decimal('100'))
        return max(repair_price, Decimal('0.00'))

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
    price = models.DecimalField(max_digits=10, decimal_places=2)
    override_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
   
    def __str__(self):
        return f"{self.quantity} x {self.get_item_name()}"

    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        ordering = ['id']

    def save(self, *args, **kwargs):
        self.full_clean()
        super(CartItem, self).save(*args, **kwargs)

    def clean(self):
        if not self.product and not self.device:
            raise ValidationError('Either product or device must be set.')
        if self.product and self.device:
            raise ValidationError('Only one of product or device can be set.')
        if self.quantity <= 0:
            raise ValidationError('Quantity must be greater than zero.')
        if self.price < 0:
            raise ValidationError('Price cannot be negative.')
        if self.override_price and self.override_price < 0:
            raise ValidationError('Override price cannot be negative.')

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
            return self.product.discounted_price
        elif self.device:
            return self.device.discounted_repair_price
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
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_tax = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
   
    def __str__(self):
        return f"Order {self.id} - {self.user.user.username}"

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']

    def update_total(self):
        subtotal = sum(item.price * item.quantity for item in self.items.all())
        total_tax = sum(item.tax_amount for item in self.items.all())
        self.total = subtotal + total_tax
        self.total_tax = total_tax
        self.save(update_fields=['total', 'total_tax'])

# =============================================================================
# OrderItem Model
# =============================================================================
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.CASCADE)
    device = models.ForeignKey(Device, null=True, blank=True, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
   
    def __str__(self):
        return f"{self.quantity} x {self.get_item_name()} in Order {self.order.id}"

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        ordering = ['order__id']

    def save(self, *args, **kwargs):
        self.full_clean()
        super(OrderItem, self).save(*args, **kwargs)
        self.calculate_tax()
        self.order.update_total()

    def delete(self, *args, **kwargs):
        super(OrderItem, self).delete(*args, **kwargs)
        self.order.update_total()

    def clean(self):
        if not self.product and not self.device:
            raise ValidationError('Either product or device must be set.')
        if self.product and self.device:
            raise ValidationError('Only one of product or device can be set.')
        if self.quantity <= 0:
            raise ValidationError('Quantity must be greater than zero.')
        if self.price < 0:
            raise ValidationError('Price cannot be negative.')

    def get_item_name(self):
        if self.product:
            return self.product.name
        elif self.device:
            return self.device.name
        return 'Unknown Item'

    def calculate_tax(self):
        is_taxable = False
        if self.product and self.product.department.is_taxable:
            is_taxable = True
        elif self.device and self.device.department and self.device.department.is_taxable:
            is_taxable = True

        if is_taxable:
            tax_rate = SALES_TAX_RATE
            self.tax_amount = (self.price * self.quantity) * tax_rate
        else:
            self.tax_amount = Decimal('0.00')
        super(OrderItem, self).save(update_fields=['tax_amount'])