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
