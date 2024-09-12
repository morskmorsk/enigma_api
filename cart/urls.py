from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

router = DefaultRouter()

router.register('profiles', views.UserProfileViewSet, basename='profile')
router.register(r'locations', views.LocationViewSet, basename='location')
router.register(r'departments', views.DepartmentViewSet, basename='department')
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'devices', views.DeviceViewSet, basename='device')
router.register(r'carts', views.CartViewSet, basename='cart')
router.register(r'cart-items', views.CartItemViewSet, basename='cart-item')

urlpatterns = [
    path('', include(router.urls)),  # Include the router-generated URLs
    path('__debug__/', include('debug_toolbar.urls')),  # Add this line
]
