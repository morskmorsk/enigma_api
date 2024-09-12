from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import UserProfile
from .serializers import UserProfileSerializer


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

# /////////////////////////////////////////////////////////////////////////////////////////////
from .models import Location, Department, Product
from .serializers import LocationSerializer, DepartmentSerializer, ProductSerializer

# Location ViewSet
class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


# Department ViewSet
class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


# Product ViewSet
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# /////////////////////////////////////////////////////////////////////////////////////////////
# device viewset
from .models import Device
from .serializers import DeviceSerializer

class DeviceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = DeviceSerializer

    def get_queryset(self):
        # Filter devices by the current authenticated user
        return Device.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        # Automatically set the device's owner to the authenticated user
        serializer.save(owner=self.request.user)
