from decimal import Decimal

from django.db import transaction
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from cart.models import Cart, CartItem, CartStatus
from cart.serializers import CartSerializer
from cart.services import CartService
from products.models import Product

from .services import get_active_price


class CartListView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get current user's cart items",
        description="Retrieve all items in the user's cart, along with total price.",
        tags=["Cart"],
        responses={
            200: CartSerializer,
            401: {"detail": "Authentication credentials were not provided."},
        },
    )
    def get(self, request):
        redis_items = CartService.get_all_items(request.user.id)
        products = Product.objects.filter(id__in=redis_items.keys())

        items_data = []
        total_amount = Decimal("0")
        for p in products:
            qty = int(redis_items[str(p.id)])
            price = get_active_price(p)
            items_data.append(
                {
                    "product_id": p.id,
                    "product_name": p.name,
                    "quantity": qty,
                    "product_price": str(price),
                }
            )
            total_amount += price * qty

        data = {
            "items": items_data,
            "total_amount": str(total_amount),
        }
        return Response(data, status=status.HTTP_200_OK)


class CartAddItemView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Add an item to the cart",
        description="Add a product to the user's cart by providing product ID and quantity.",
        tags=["Cart"],
        parameters=[
            OpenApiParameter(
                name="product_id", type=int, required=True, description="Product ID"
            ),
            OpenApiParameter(
                name="quantity", type=int, required=False, description="Quantity"
            ),
        ],
        responses={
            200: {"detail": "Item added to cart"},
            400: {"detail": "Validation errors"},
        },
    )
    def post(self, request):
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity", 1)

        if not product_id:
            return Response(
                {"detail": "product_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            quantity = int(quantity)
        except ValueError:
            return Response(
                {"detail": "quantity must be an integer"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if quantity <= 0:
            return Response(
                {"detail": "quantity must be > 0"}, status=status.HTTP_400_BAD_REQUEST
            )

        CartService.add_item(request.user.id, product_id, quantity)
        return Response({"detail": "Item added to cart"}, status=status.HTTP_200_OK)
