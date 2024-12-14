from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions

from .models import Category
from .serializers import CategorySerializer


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
    queryset = Category.objects.filter(is_active=True)


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
    queryset = Category.objects.all()
    permission_classes = [permissions.IsAdminUser]

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
