from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema
from drf_spectacular.views import SpectacularAPIView
from rest_framework import generics, permissions
from rest_framework.filters import SearchFilter
from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import AllowAny, IsAdminUser

from products.models import Media, Product, ProductInventory
from products.models.attribute import (
    ProductAttribute,
    ProductAttributeValue,
    ProductType,
)

from .models import (
    Product,
    ProductAttribute,
    ProductAttributeValue,
    ProductInventory,
    ProductType,
)
from .serializers import (
    AdminProductAttributeDetailSerializer,
    AdminProductAttributeSerializer,
    AdminProductAttributeValueDetailSerializer,
    AdminProductAttributeValueSerializer,
    AdminProductDetailSerializer,
    AdminProductInventoryDetailSerializer,
    AdminProductInventorySerializer,
    AdminProductMediaDetailSerializer,
    AdminProductMediaSerializer,
    AdminProductSerializer,
    AdminProductTypeDetailSerializer,
    AdminProductTypeSerializer,
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
from .utils.pagination import NoCountPagination

# ---------------------------- Create schema for swagger ----------------------------
products_schema_view = SpectacularAPIView.as_view(urlconf="products.urls")


# ---------------------------------------------------------
# User Endpoints (Products)
# ---------------------------------------------------------
@extend_schema(tags=["Product - List"])
class ProductListView(ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    queryset = Product.objects.filter(is_active=True).only("id", "name", "description")

    # Filter based on model fields:
    filter_backends = [DjangoFilterBackend, SearchFilter]

    # Filter by brand and category
    filterset_fields = ["brand", "category"]

    # Search in name and description
    search_fields = ["name", "description"]

    # use custom pagination class
    pagination_class = NoCountPagination


@extend_schema(tags=["Product - List"])
class ProductDetailView(RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]
    # By default, RetrieveAPIView uses 'pk' lookup, so {id} will be interpreted as pk.
    # If needed, you can specify lookup_field = 'id'.


@extend_schema(tags=["Product - Media"])
class ProductMediaListView(ListAPIView):
    serializer_class = MediaSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        product_id = self.kwargs.get("pk")
        product = get_object_or_404(Product, pk=product_id, is_active=True)
        # Return all media objects related to this product
        return product.media.all().order_by("ordering")


@extend_schema(tags=["Product - Inventory"])
class ProductInventoryListView(ListAPIView):
    serializer_class = ProductInventorySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        product_id = self.kwargs.get("pk")
        product = get_object_or_404(Product, pk=product_id, is_active=True)
        return ProductInventory.objects.filter(product=product).order_by("created_at")


@extend_schema(tags=["Product - Types"])
class ProductTypeListView(ListAPIView):
    serializer_class = ProductTypeSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return ProductType.objects.all().order_by("name")


@extend_schema(tags=["Product - Types"])
class ProductTypeDetailView(RetrieveAPIView):
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeDetailSerializer
    permission_classes = [AllowAny]
    # By default, RetrieveAPIView uses "pk" as lookup_field, so {id} in the URL maps to the product type's primary key.


@extend_schema(tags=["Product - Attributes"])
class ProductAttributeListView(ListAPIView):
    queryset = ProductAttribute.objects.all()
    serializer_class = ProductAttributeSerializer
    permission_classes = [AllowAny]


@extend_schema(tags=["Product - Attributes"])
class ProductAttributeDetailView(RetrieveAPIView):
    queryset = ProductAttribute.objects.all()
    serializer_class = ProductAttributeDetailSerializer
    permission_classes = [AllowAny]


@extend_schema(tags=["Product - Attributes"])
class ProductAttributeValueListView(ListAPIView):
    serializer_class = ProductAttributeValueSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        attribute_id = self.kwargs.get("attribute_id")
        attribute = get_object_or_404(ProductAttribute, pk=attribute_id)
        return ProductAttributeValue.objects.filter(
            product_attribute=attribute
        ).order_by("id")


@extend_schema(tags=["Product - Attributes"])
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


# ---------------------------------------------------------
# Admin Endpoints (Products)
# ---------------------------------------------------------
@extend_schema(
    tags=["Admin - Product"],
    summary="List or create products",
    parameters=[
        OpenApiParameter(
            name="search",
            description="Search products by name",
            required=False,
            type=str,
        ),
        OpenApiParameter(
            name="page",
            description="Page number for pagination",
            required=False,
            type=int,
        ),
    ],
)
class AdminProductListCreateView(ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = AdminProductSerializer
    permission_classes = [IsAdminUser]


@extend_schema(
    tags=["Admin - Product"],
    summary="View, update, or delete a specific product",
)
class AdminProductDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = AdminProductDetailSerializer
    permission_classes = [IsAdminUser]


@extend_schema(
    tags=["Admin - Product Media"],
    summary="List or create product media",
)
class AdminProductMediaListCreateView(ListCreateAPIView):
    serializer_class = AdminProductMediaSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        product_id = self.kwargs.get("id")
        return Media.objects.filter(product_id=product_id)

    def perform_create(self, serializer):
        product_id = self.kwargs.get("id")
        product = Product.objects.get(pk=product_id)
        serializer.save(product=product)


@extend_schema(
    tags=["Admin - Product Media"],
    summary="View, update, or delete a specific product media",
)
class AdminProductMediaDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Media.objects.all()
    serializer_class = AdminProductMediaDetailSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        product_id = self.kwargs.get("product_id")
        return Media.objects.filter(product_id=product_id)


@extend_schema(
    tags=["Admin - Product Inventory"],
    summary="List or create product inventories",
)
class AdminProductInventoryListCreateView(ListCreateAPIView):
    queryset = ProductInventory.objects.all()
    serializer_class = AdminProductInventorySerializer
    permission_classes = [IsAdminUser]


@extend_schema(
    tags=["Admin - Product Inventory"],
    summary="View, update, or delete a specific product inventory",
)
class AdminProductInventoryDetailView(RetrieveUpdateDestroyAPIView):
    queryset = ProductInventory.objects.all()
    serializer_class = AdminProductInventoryDetailSerializer
    permission_classes = [IsAdminUser]
    lookup_field = "sku"  # Retrieve inventory by SKU


@extend_schema(
    tags=["Admin - Product Types"],
    summary="List or create product types",
)
class AdminProductTypeListCreateView(ListCreateAPIView):
    queryset = ProductType.objects.all()
    serializer_class = AdminProductTypeSerializer
    permission_classes = [IsAdminUser]


@extend_schema(
    tags=["Admin - Product Types"],
    summary="View, update, or delete a product type",
)
class AdminProductTypeDetailView(RetrieveUpdateDestroyAPIView):
    queryset = ProductType.objects.all()
    serializer_class = AdminProductTypeDetailSerializer
    permission_classes = [IsAdminUser]


@extend_schema(
    tags=["Admin - Product Attributes"],
    summary="List or create product attributes",
)
class AdminProductAttributeListCreateView(ListCreateAPIView):
    queryset = ProductAttribute.objects.all()
    serializer_class = AdminProductAttributeSerializer
    permission_classes = [IsAdminUser]


@extend_schema(
    tags=["Admin - Product Attributes"],
    summary="View, update, or delete a product attribute",
)
class AdminProductAttributeDetailView(RetrieveUpdateDestroyAPIView):
    queryset = ProductAttribute.objects.all()
    serializer_class = AdminProductAttributeDetailSerializer
    permission_classes = [IsAdminUser]


@extend_schema(
    tags=["Admin - Product Attributes"],
    summary="List or create attribute values for a specific product attribute",
    parameters=[
        OpenApiParameter(
            name="attribute_id",
            description="ID of the product attribute",
            required=True,
            type=int,
        )
    ],
)
class AdminProductAttributeValueListCreateView(generics.ListCreateAPIView):
    serializer_class = AdminProductAttributeValueSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        attribute_id = self.kwargs.get("attribute_id")
        return ProductAttributeValue.objects.filter(
            product_attribute_id=attribute_id
        ).order_by("id")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["attribute_id"] = self.kwargs.get("attribute_id")
        return context


@extend_schema(
    tags=["Admin - Product Attributes"],
    summary="View, update, or delete a specific attribute value",
    parameters=[
        OpenApiParameter(
            name="attribute_id",
            description="ID of the product attribute",
            required=True,
            type=int,
        ),
        OpenApiParameter(
            name="pk",
            description="ID of the product attribute value",
            required=True,
            type=int,
        ),
    ],
)
class AdminProductAttributeValueDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = AdminProductAttributeValueDetailSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        attribute_id = self.kwargs["attribute_id"]
        return ProductAttributeValue.objects.filter(product_attribute_id=attribute_id)
