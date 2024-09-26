from django.contrib import admin
from .models import Cart, CartItem, Department, Location, Order, OrderItem, Product, UserProfile, Device

# =================================================================================================

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'carrier', 'monthly_payment']
    search_fields = ['user__username', 'phone_number', 'carrier']
    list_filter = ['carrier']
    list_per_page = 10

# =================================================================================================

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at', 'updated_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']
    list_per_page = 10
    date_hierarchy = 'created_at'
    ordering = ['name']

# =================================================================================================

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_taxable', 'created_at', 'updated_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at', 'is_taxable']
    list_per_page = 10
    date_hierarchy = 'created_at'
    ordering = ['name']

# =================================================================================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'price', 'location', 'department', 'is_available', 'on_hand', 'cost',
        'created_at', 'updated_at'
    ]
    search_fields = ['name', 'description']
    list_filter = ['created_at', 'location', 'department', 'is_available', 'sale_start', 'sale_end']
    list_per_page = 10
    date_hierarchy = 'created_at'
    ordering = ['name']
    # Removed readonly_fields attribute

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['created_at', 'updated_at']
        return []

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('location', 'department')

# =================================================================================================

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'updated_at']
    search_fields = ['user__user__username']  # Corrected field lookup
    list_filter = ['created_at']
    list_per_page = 10
    date_hierarchy = 'created_at'
    ordering = ['user__user__username']  # Corrected field lookup

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user__user')  # Corrected field lookup

# =================================================================================================

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = [
        'cart', 'get_item_name', 'quantity', 'effective_price', 'total_price',
        'created_at', 'updated_at'
    ]
    search_fields = [
        'cart__user__user__username',  # Corrected field lookup
        'product__name',
        'device__name'
    ]
    list_filter = ['created_at']
    ordering = ['cart__user__user__username', 'product__name', 'device__name']  # Corrected field lookup

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('cart__user__user', 'product', 'device')  # Corrected field lookup

    def get_item_name(self, obj):
        return obj.get_item_name()
    get_item_name.short_description = 'Item'

# =================================================================================================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'total', 'total_tax', 'created_at', 'updated_at']
    search_fields = ['user__user__username']  # Corrected field lookup
    list_filter = ['created_at', 'status']
    list_per_page = 10
    date_hierarchy = 'created_at'
    ordering = ['user__user__username']  # Corrected field lookup

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user__user')  # Corrected field lookup

# =================================================================================================

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'get_item_name', 'quantity', 'price', 'tax_amount']
    search_fields = [
        'order__user__user__username',  # Corrected field lookup
        'product__name',
        'device__name'
    ]
    list_filter = ['order__created_at']
    list_per_page = 10
    date_hierarchy = 'order__created_at'
    ordering = ['order__user__user__username', 'product__name', 'device__name']  # Corrected field lookup

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('order__user__user', 'product', 'device')  # Corrected field lookup

    def get_item_name(self, obj):
        return obj.get_item_name()
    get_item_name.short_description = 'Item'

# =================================================================================================

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = [
        'owner', 'name', 'device_model', 'imei', 'serial_number', 'location',
        'department', 'created_at', 'updated_at'
    ]
    search_fields = [
        'owner__user__username',  # Corrected field lookup
        'name', 'device_model', 'imei', 'serial_number'
    ]
    list_filter = ['created_at', 'location', 'department']
    list_per_page = 10
    date_hierarchy = 'created_at'
    ordering = ['owner__user__username', 'name', 'device_model']  # Corrected field lookup
    # Removed readonly_fields attribute

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['created_at', 'updated_at']
        return []

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('owner__user', 'location', 'department')  # Corrected field lookup

# =================================================================================================