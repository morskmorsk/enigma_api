from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

router = DefaultRouter()

router.register('profiles', views.UserProfileViewSet)


urlpatterns = [
    path('', include(router.urls)),  # Include the router-generated URLs
    path('__debug__/', include('debug_toolbar.urls')),  # Add this line
]
