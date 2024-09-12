from django.contrib import admin
from .models import Cart, CartItem, Department, Location, Order, OrderItem, Product, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'carrier', 'monthly_payment']
    search_fields = ['user__username', 'phone_number', 'carrier']
    list_filter = ['phone_number']
    list_per_page = 10

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at', 'updated_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']
    list_per_page = 10
    date_hierarchy = 'created_at'
    ordering = ['name']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_taxable', 'created_at', 'updated_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']
    list_per_page = 10
    date_hierarchy = 'created_at'
    ordering = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'location', 'department', 'is_available', 'on_hand', 'cost', 'created_at', 'updated_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at', 'location', 'department']
    list_per_page = 10
    date_hierarchy = 'created_at'
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['created_at', 'updated_at']
        return []

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('location', 'department')


# /////////////////////////////////////////////////////////////////////////////////////////////

# Cart and CartItem models
# class Cart(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"Cart for {self.user.username}"

#     @property
#     def total(self):
#         return sum(item.total_price for item in self.items.all())


# class CartItem(models.Model):
#     cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)

#     # Generic ForeignKey to allow Product or Device
#     content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
#     object_id = models.PositiveIntegerField()
#     content_object = GenericForeignKey('content_type', 'object_id')

#     quantity = models.PositiveIntegerField(default=1)
#     override_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
#     effective_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.quantity} x {self.content_object}"

#     @property
#     def effective_price(self):
#         if hasattr(self.content_object, 'price'):
#             return self.override_price if self.override_price is not None else self.content_object.price
#         elif hasattr(self.content_object, 'repair_price'):
#             return self.override_price if self.override_price is not None else self.content_object.repair_price
#         return Decimal('0.00')

#     @property
#     def total_price(self):
#         return self.effective_price * self.quantity


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'updated_at']
    search_fields = ['user__username']
    list_filter = ['created_at']
    list_per_page = 10
    date_hierarchy = 'created_at'
    ordering = ['user__username']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'content_object', 'quantity', 'effective_price', 'total_price', 'created_at', 'updated_at']
    search_fields = ['cart__user__username', 'content_object__name']
    list_filter = ['created_at']
    list_per_page = 10
    date_hierarchy = 'created_at'
    ordering = ['cart__user__username', 'content_object__name']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('cart__user', 'content_type').prefetch_related('content_object')

# /////////////////////////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////////////////////
# # Order and OrderItem models
# class Order(models.Model):
#     STATUS_CHOICES = (
#         ('pending', 'Pending'),
#         ('processing', 'Processing'),
#         ('shipped', 'Shipped'),
#         ('delivered', 'Delivered'),
#         ('cancelled', 'Cancelled'),
#     )

#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
#     total = models.DecimalField(max_digits=10, decimal_places=2)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"Order {self.id} - {self.user.username}"


# class OrderItem(models.Model):
#     order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField()
#     price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at the time of purchase

#     def __str__(self):
#         return f"{self.quantity} x {self.product.name} in Order {self.order.id}"
# /////////////////////////////////////////////////////////////////////////////////////////////


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'total', 'created_at', 'updated_at']
    search_fields = ['user__username']
    list_filter = ['created_at', 'status']
    list_per_page = 10
    date_hierarchy = 'created_at'
    ordering = ['user__username']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price']
    search_fields = ['order__user__username', 'product__name']
    list_filter = ['order__created_at']
    list_per_page = 10
    date_hierarchy = 'order__created_at'
    ordering = ['order__user__username', 'product__name']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('order__user', 'product')
    