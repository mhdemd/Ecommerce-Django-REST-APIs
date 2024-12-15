from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAdminUser

from .models import Brand
from .serializers import BrandSerializer


# ---------------------------------------------------------
# User Endpoints (Brands)
# ---------------------------------------------------------
class BrandListView(ListAPIView):
    """
    List of brands (for users)
    """

    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


class BrandDetailView(RetrieveAPIView):
    """
    Details of a specific brand (for users)
    """

    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


# ---------------------------------------------------------
# Admin Endpoints (Brands)
# ---------------------------------------------------------
class AdminBrandListCreateView(ListCreateAPIView):
    """
    List and create a brand (admin only)
    """

    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAdminUser]


class AdminBrandDetailView(RetrieveUpdateDestroyAPIView):
    """
    View details, edit or delete brand (admin only)
    """

    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAdminUser]
