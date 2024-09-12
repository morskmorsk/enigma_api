from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

router = DefaultRouter()

router.register('profiles', views.UserProfileViewSet)
router.register(r'locations', views.LocationViewSet)
router.register(r'departments', views.DepartmentViewSet)
router.register(r'products', views.ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),  # Include the router-generated URLs
    path('__debug__/', include('debug_toolbar.urls')),  # Add this line
]
