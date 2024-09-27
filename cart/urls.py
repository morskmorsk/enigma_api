from django.conf import settings
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from . import views

router = DefaultRouter()

router.register(r'userprofiles', views.UserProfileViewSet, basename='userprofile')
router.register(r'locations', views.LocationViewSet, basename='location')
router.register(r'departments', views.DepartmentViewSet, basename='department')
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'devices', views.DeviceViewSet, basename='device')
router.register(r'cart', views.CartViewSet, basename='cart')
router.register(r'cart-items', views.CartItemViewSet, basename='cartitem')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'order-items', views.OrderItemViewSet, basename='orderitem')

urlpatterns = [
    path('', include(router.urls)),  # Include the router-generated URLs
    path('api-token-auth/', obtain_auth_token),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]