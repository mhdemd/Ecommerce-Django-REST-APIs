from rest_framework import serializers

from .models import Media, Product, ProductInventory


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
