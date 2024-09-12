from django.contrib import admin
from .models import Department, Location, Product, UserProfile


# # location model
# class Location(models.Model):
#     name = models.CharField(max_length=200)
#     description = models.TextField(blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.name

# #  department model
# class Department(models.Model):
#     name = models.CharField(max_length=200)
#     description = models.TextField(blank=True)
#     is_taxable = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.name

# #  product model
# class Product(models.Model):
#     name = models.CharField(max_length=200)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     description = models.TextField(blank=True)
#     image = models.ImageField(upload_to='products/', blank=True)
#     barcode = models.CharField(max_length=100, blank=True, null=True, unique=True)
#     location = models.ForeignKey(Location, on_delete=models.CASCADE)
#     department = models.ForeignKey(Department, on_delete=models.CASCADE)
#     is_available = models.BooleanField(default=True)
#     on_hand = models.IntegerField(default=0)
#     cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.name

#     def clean(self):
#             super().clean()
#             # Validate the image file type and size
#             if self.image:
#                 if not self.image.name.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.webp')):
#                     raise ValidationError('Only .jpg, .jpeg, .tiff, .webp and .png files are allowed.')
#                 if self.image.size > 5 * 1024 * 1024:  # Limit size to 5 MB
#                     raise ValidationError('The image file size cannot exceed 5 MB.')

#     def update_inventory(self, inventory_quantity):
#         self.on_hand = inventory_quantity
#         self.save()

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
