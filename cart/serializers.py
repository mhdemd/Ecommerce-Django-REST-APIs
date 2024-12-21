from rest_framework import serializers

from products.models import Product

from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product", write_only=True
    )
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_price = serializers.DecimalField(
        source="price", max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = CartItem
        fields = ["id", "product_id", "product_name", "quantity", "product_price"]
