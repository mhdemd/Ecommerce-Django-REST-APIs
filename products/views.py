from django.db.models import Q
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny

from .models import (
    Media,
    Product,
    ProductAttribute,
    ProductAttributeValue,
    ProductInventory,
    ProductType,
)
from .serializers import (
    MediaSerializer,
    ProductAttributeDetailSerializer,
    ProductAttributeSerializer,
    ProductAttributeValueDetailSerializer,
    ProductAttributeValueSerializer,
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


class ProductAttributeListView(ListAPIView):
    queryset = ProductAttribute.objects.all()
    serializer_class = ProductAttributeSerializer
    permission_classes = [AllowAny]


class ProductAttributeDetailView(RetrieveAPIView):
    queryset = ProductAttribute.objects.all()
    serializer_class = ProductAttributeDetailSerializer
    permission_classes = [AllowAny]


class ProductAttributeValueListView(ListAPIView):
    serializer_class = ProductAttributeValueSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        attribute_id = self.kwargs.get("attribute_id")
        attribute = get_object_or_404(ProductAttribute, pk=attribute_id)
        return ProductAttributeValue.objects.filter(
            product_attribute=attribute
        ).order_by("id")


class ProductAttributeValueDetailView(RetrieveAPIView):
    serializer_class = ProductAttributeValueDetailSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        attribute_id = self.kwargs.get("attribute_id")
        value_id = self.kwargs.get("value_id")
        # Ensure the attribute exists
        attribute = get_object_or_404(ProductAttribute, pk=attribute_id)
        # Then ensure the value belongs to this attribute
        return get_object_or_404(
            ProductAttributeValue, pk=value_id, product_attribute=attribute
        )
