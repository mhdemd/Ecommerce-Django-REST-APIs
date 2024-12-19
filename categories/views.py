from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from drf_spectacular.views import SpectacularAPIView
from rest_framework import filters, generics, permissions

from .models import Category
from .serializers import CategorySerializer

# ---------------------------- Create schema for swagger ----------------------------
category_schema_view = SpectacularAPIView.as_view(urlconf="categories.urls")


# -------------------------
# User Endpoints
# -------------------------
@extend_schema(tags=["Category - List"])
class CategoryListView(generics.ListAPIView):
    """
    Returns a list of all active categories.
    Only active categories are visible to the end user.
    """

    serializer_class = CategorySerializer
    queryset = Category.objects.filter(is_active=True).select_related(
        "parent", "children"
    )

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["name", "parent"]  # Fields available for filtering
    search_fields = ["name"]  # Fields available for search
    ordering_fields = ["name", "created_at"]  # Fields available for ordering
    ordering = ["name"]  # Default ordering


@extend_schema(tags=["Category - Detail"])
class CategoryDetailView(generics.RetrieveAPIView):
    """
    Returns the details of a single active category by its primary key (pk).
    """

    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(is_active=True)

    def get_object(self):
        queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.kwargs.get("pk"))


# -------------------------
# Admin Endpoints
# -------------------------
@extend_schema(tags=["Admin - Category"])
class AdminCategoryListCreateView(generics.ListCreateAPIView):
    """
    Allows admin to list and create categories.
    Requires admin privileges.
    """

    serializer_class = CategorySerializer
    queryset = Category.objects.select_related("parent").prefetch_related("children")

    permission_classes = [permissions.IsAdminUser]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["name", "is_active", "parent"]  # Fields available for filtering
    search_fields = ["name"]  # Fields available for search
    ordering_fields = ["name", "created_at"]  # Fields available for ordering
    ordering = ["-created_at"]  # Default ordering

    def perform_create(self, serializer):
        serializer.save()


@extend_schema(tags=["Admin - Category"])
class AdminCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Allows admin to retrieve, update or delete a specific category by pk.
    Requires admin privileges.
    """

    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["name", "is_active", "parent"]  # Fields available for filtering
    search_fields = ["name"]  # Fields available for search
    ordering_fields = ["name", "created_at"]  # Fields available for ordering
    ordering = ["-created_at"]  # Default ordering
