from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
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
    List of brands (for users) with filtering, searching, and ordering
    """

    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["name", "slug"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]


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
    List and create a brand (admin only) with filtering, searching, and ordering
    """

    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["name", "slug"]  # Fields for filtering
    search_fields = ["name", "description"]  # Fields for searching
    ordering_fields = ["name", "created_at"]  # Fields for sorting
    ordering = ["name"]  # Default ordering


class AdminBrandDetailView(RetrieveUpdateDestroyAPIView):
    """
    View details, edit or delete brand (admin only)
    """

    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAdminUser]
