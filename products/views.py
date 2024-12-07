from django.db.models import Q
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny

from .models import Media, Product, ProductInventory, ProductType
from .serializers import (
    MediaSerializer,
    ProductDetailSerializer,
    ProductInventorySerializer,
    ProductSerializer,
    ProductTypeDetailSerializer,
    ProductTypeSerializer,
)


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


class ProductDetailView(RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]
    # By default, RetrieveAPIView uses 'pk' lookup, so {id} will be interpreted as pk.
    # If needed, you can specify lookup_field = 'id'.


class ProductMediaListView(ListAPIView):
    serializer_class = MediaSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        product_id = self.kwargs.get("pk")
        product = get_object_or_404(Product, pk=product_id, is_active=True)
        # Return all media objects related to this product
        return product.media.all().order_by("ordering")


class ProductInventoryListView(ListAPIView):
    serializer_class = ProductInventorySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        product_id = self.kwargs.get("pk")
        product = get_object_or_404(Product, pk=product_id, is_active=True)
        return ProductInventory.objects.filter(product=product).order_by("created_at")


class ProductTypeListView(ListAPIView):
    serializer_class = ProductTypeSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return ProductType.objects.all().order_by("name")


class ProductTypeDetailView(RetrieveAPIView):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeDetailSerializer
    permission_classes = [AllowAny]
    # By default, RetrieveAPIView uses "pk" as lookup_field, so {id} in the URL maps to the product type's primary key.
