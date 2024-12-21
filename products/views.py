from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema
from drf_spectacular.views import SpectacularAPIView
from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound
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

# ---------------------------- Create schema for swagger ----------------------------
products_schema_view = SpectacularAPIView.as_view(urlconf="products.urls")


# ---------------------------------------------------------
# User Endpoints (Products)
# ---------------------------------------------------------
@extend_schema(tags=["Product - List"])
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


@extend_schema(tags=["Product - List"])
class ProductDetailView(RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True).select_related(
        "category", "brand"
    )
    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]


@extend_schema(tags=["Product - Media"])
class ProductMediaListView(ListAPIView):
    serializer_class = MediaSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        product_id = self.kwargs.get("pk")

        # Ensure the product exists and is active
        product = get_object_or_404(Product, id=product_id, is_active=True)

        # Return the media for the product
        return Media.objects.filter(product=product).order_by("ordering")


@extend_schema(tags=["Product - Inventory"])
class ProductInventoryListView(ListAPIView):
    serializer_class = ProductInventorySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        product_id = self.kwargs.get("pk")

        # Use get_object_or_404 to ensure product exists and is active
        product = get_object_or_404(Product, id=product_id, is_active=True)

        # Return the inventory queryset
        queryset = (
            ProductInventory.objects.filter(product=product)
            .select_related("product")
            .prefetch_related(
                Prefetch(
                    "attribute_values",
                    queryset=ProductAttributeValue.objects.select_related(
                        "product_attribute"
                    ),
                )
            )
            .order_by("id")  # Order results by ID for predictability
        )
        return queryset


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

        # Filter ProductAttributeValue and ensure ProductAttribute exists
        queryset = ProductAttributeValue.objects.filter(
            product_attribute_id=attribute_id
        ).select_related("product_attribute")

        # If no ProductAttributeValue exists, ensure the ProductAttribute exists
        if (
            not queryset.exists()
            and not ProductAttribute.objects.filter(pk=attribute_id).exists()
        ):
            raise NotFound(detail="Product attribute not found.", code=404)

        return queryset


@extend_schema(tags=["Product - Attributes"])
class ProductAttributeValueDetailView(RetrieveAPIView):
    serializer_class = ProductAttributeValueDetailSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        attribute_id = self.kwargs.get("attribute_id")
        value_id = self.kwargs.get("value_id")

        return get_object_or_404(
            ProductAttributeValue.objects.select_related("product_attribute"),
            product_attribute__id=attribute_id,
            pk=value_id,
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

        # Check if any Media exists for the given product_id
        queryset = Media.objects.filter(product_id=product_id)
        if not Product.objects.filter(pk=product_id).exists():
            raise NotFound(detail="Product not found.", code=404)

        return queryset

    def perform_create(self, serializer):
        product_id = self.kwargs.get("id")

        # Ensure the product exists before creating media
        if not Product.objects.filter(pk=product_id).exists():
            raise NotFound(detail="Product not found.", code=404)

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

        # Filter Media and ensure product exists in a single query
        queryset = Media.objects.filter(product__id=product_id)

        # Check if queryset is empty (product doesn't exist or no media linked)
        if not queryset.exists():
            if not Product.objects.filter(pk=product_id).exists():
                raise NotFound(detail="Product not found.", code=404)

        return queryset


@extend_schema(
    tags=["Admin - Product Inventory"],
    summary="List or create product inventories",
)
class AdminProductInventoryListCreateView(ListCreateAPIView):
    queryset = ProductInventory.objects.prefetch_related(
        Prefetch(
            "attribute_values",
            queryset=ProductAttributeValue.objects.select_related("product_attribute"),
        )
    )
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
)
class AdminProductAttributeValueListCreateView(generics.ListCreateAPIView):
    serializer_class = AdminProductAttributeValueSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        attribute_id = self.kwargs.get("attribute_id")

        # Filter and ensure the attribute exists in one optimized step
        queryset = ProductAttributeValue.objects.filter(
            product_attribute_id=attribute_id
        ).order_by("id")

        # Check if the attribute exists only if the queryset is empty
        if not queryset.exists():
            if not ProductAttribute.objects.filter(pk=attribute_id).exists():
                raise NotFound(detail="Product attribute not found.", code=404)

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["attribute_id"] = self.kwargs.get("attribute_id")
        return context


@extend_schema(
    tags=["Admin - Product Attributes"],
    summary="View, update, or delete a specific attribute value",
)
class AdminProductAttributeValueDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = AdminProductAttributeValueDetailSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        attribute_id = self.kwargs["attribute_id"]

        # Filter values and ensure the attribute exists if the queryset is empty
        queryset = ProductAttributeValue.objects.filter(
            product_attribute_id=attribute_id
        )
        if not queryset.exists():  # Check if there are no values
            if not ProductAttribute.objects.filter(pk=attribute_id).exists():
                raise NotFound(detail="Product attribute not found.", code=404)

        return queryset
