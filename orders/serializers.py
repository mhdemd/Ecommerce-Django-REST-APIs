from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "price"]


class OrderSerializer(serializers.ModelSerializer):
    item = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        field = [
            "id",
            "user",
            "status",
            "total_amount",
            "craeted_at",
            "updated_at",
            "items",
        ]
