from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from drf_spectacular.views import SpectacularAPIView
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

# ---------------------------- Create schema for swagger ----------------------------
brands_schema_view = SpectacularAPIView.as_view(urlconf="brands.urls")


# ---------------------------------------------------------
# User Endpoints (Brands)
# ---------------------------------------------------------
@extend_schema(
    tags=["Brand - List"],
    operation_id="list_brands_for_users",
    description="Retrieve a list of brands with filtering, searching, and ordering capabilities.",
)
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


@extend_schema(
    tags=["Brand - Detail"],
    operation_id="retrieve_brand_detail_for_users",
    description="Retrieve detailed information about a specific brand.",
)
class BrandDetailView(RetrieveAPIView):
    """
    Details of a specific brand (for users)
    """

    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


# ---------------------------------------------------------
# Admin Endpoints (Brands)
# ---------------------------------------------------------
@extend_schema(
    tags=["Admin - Brand"],
    operation_id="admin_list_and_create_brands",
    description="List and create brands with filtering, searching, and ordering capabilities (admin only).",
)
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


@extend_schema(
    tags=["Admin - Brand"],
    operation_id="admin_manage_brand_detail",
    description="View, edit, or delete a specific brand (admin only).",
)
class AdminBrandDetailView(RetrieveUpdateDestroyAPIView):
    """
    View details, edit or delete brand (admin only)
    """

    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAdminUser]
