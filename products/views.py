from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from .models import Product
from .serializers import ProductSerializer


class ProductListView(ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    queryset = Product.objects.filter(is_active=True)

    # Filter based on model fields:
    filter_backends = [DjangoFilterBackend, SearchFilter]

    # Filter by brand and category
    filterset_fields = ["brand", "category"]

    # Search in name and description
    search_fields = ["name", "description"]
