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
# =============================================================================
# class OrderViewSet(viewsets.ModelViewSet):
#     serializer_class = OrderSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         profile = get_user_profile(self.request)
#         return Order.objects.filter(user=profile)

#     def perform_create(self, serializer):
#         profile = get_user_profile(self.request)
#         order = serializer.save(user=profile)
#         # The order total and tax are updated automatically when OrderItems are added

#     @action(detail=False, methods=['post'])
#     def place_order(self, request):
#         profile = get_user_profile(request)
#         cart = assign_cart_to_user(profile)
#         if not cart.items.exists():
#             return Response({'detail': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

#         order = Order.objects.create(user=profile, status='pending')
#         for cart_item in cart.items.all():
#             order_item = OrderItem.objects.create(
#                 order=order,
#                 product=cart_item.product,
#                 device=cart_item.device,
#                 quantity=cart_item.quantity,
#                 price=cart_item.effective_price,
#             )
#             # Tax calculation is handled in OrderItem's save method

#         # Order total and tax are updated automatically
#         # Clear the cart
#         cart.items.all().delete()
#         serializer = self.get_serializer(order)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

#     @action(detail=False, methods=['get'])
#     def user(self, request):
#         profile = get_user_profile(request)
#         orders = Order.objects.filter(user=profile)
#         serializer = self.get_serializer(orders, many=True)
#         return Response(serializer.data)
# =============================================================================
urlpatterns = [
    path('', include(router.urls)),  # Include the router-generated URLs
    path('api-token-auth/', obtain_auth_token),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('place-order/', views.OrderViewSet.as_view({'post': 'place_order'}), name='place-order'),
    path('my-orders/', views.OrderViewSet.as_view({'get': 'user'}), name='my-orders'),    
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]