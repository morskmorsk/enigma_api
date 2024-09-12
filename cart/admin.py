from django.contrib import admin
from .models import UserProfile

# # models.py
# from django.db import models
# from django.contrib.auth.models import User

# # User profile model for phone number, carrier, and monthly payment
# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
#     phone_number = models.CharField(max_length=20, blank=True)
#     carrier = models.CharField(max_length=100, blank=True, null= True)  # New field for carrier
#     monthly_payment = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # New field for monthly payment

#     def __str__(self):
#         return f"{self.user.username}'s profile"

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'carrier', 'monthly_payment']
    search_fields = ['user__username', 'phone_number', 'carrier']