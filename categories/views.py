from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions

from .models import Category
from .permissions import IsAdminUserOrReadOnly
from .serializers import CategorySerializer


# -------------------------
# User Endpoints
# -------------------------
class CategoryListView(generics.ListAPIView):
    """
    Returns a list of all active categories.
    Only active categories are visible to the end user.
    """

    serializer_class = CategorySerializer
    queryset = Category.objects.filter(is_active=True)


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


class AdminCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Allows admin to retrieve, update or delete a specific category by pk.
    Requires admin privileges.
    """

    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = [permissions.IsAdminUser]
