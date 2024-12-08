from rest_framework import serializers

from products.models import Media, Product, ProductInventory
from products.models.attribute import ProductType

from .models import (
    Media,
    Product,
    ProductAttribute,
    ProductAttributeValue,
    ProductInventory,
    ProductType,
)


# ---------------------------------------------------------
# User Endpoints (Products)
# ---------------------------------------------------------
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "web_id",
            "slug",
            "name",
            "description",
            "brand",
            "category",
            "is_active",
            "created_at",
            "updated_at",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source="brand.name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "web_id",
            "slug",
            "name",
            "description",
            "brand",
            "brand_name",
            "category",
            "category_name",
            "is_active",
            "created_at",
            "updated_at",
        ]
        # brand and category are included as IDs, but brand_name and category_name
        # provide a human-readable form.


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ["id", "image", "is_feature", "ordering", "created_at", "updated_at"]


class ProductInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductInventory
        fields = [
            "id",
            "sku",
            "upc",
            "stock",
            "retail_price",
            "store_price",
            "sale_price",
            "weight",
            "is_active",
            "created_at",
            "updated_at",
        ]


class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = ["id", "name", "slug"]


class ProductTypeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = ["id", "name", "slug"]


class ProductAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttribute
        fields = ["id", "name", "description", "created_at", "updated_at"]


class ProductAttributeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttribute
        fields = ["id", "name", "description", "created_at", "updated_at"]


class ProductAttributeValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttributeValue
        fields = ["id", "attribute_value", "created_at", "updated_at"]


class ProductAttributeValueDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttributeValue
        fields = ["id", "attribute_value", "created_at", "updated_at"]


# ---------------------------------------------------------
# Admin Endpoints (Products)
# ---------------------------------------------------------
class AdminProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "web_id",
            "slug",
            "name",
            "description",
            "brand",
            "category",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AdminProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "web_id",
            "slug",
            "name",
            "description",
            "brand",
            "category",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AdminProductMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = [
            "id",
            "product",
            "image",
            "is_feature",
            "ordering",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AdminProductMediaDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = [
            "id",
            "product",
            "image",
            "is_feature",
            "ordering",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "product", "created_at", "updated_at"]


class AdminProductInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductInventory
        fields = [
            "id",
            "sku",
            "upc",
            "product",
            "product_type",
            "attribute_values",
            "stock",
            "is_active",
            "retail_price",
            "store_price",
            "sale_price",
            "weight",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AdminProductInventoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductInventory
        fields = [
            "id",
            "sku",
            "upc",
            "product",
            "product_type",
            "attribute_values",
            "stock",
            "is_active",
            "retail_price",
            "store_price",
            "sale_price",
            "weight",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AdminProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = ["id", "name", "slug"]
        read_only_fields = ["id"]


class AdminProductTypeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = ["id", "name", "slug"]
        read_only_fields = ["id"]
