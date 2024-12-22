from decimal import Decimal

from django.db import transaction
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from cart.models import Cart, CartItem, CartStatus
from cart.serializers import CartSerializer
from cart.services import CartService
from products.models import Product

from .services import get_active_price


class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get current user's cart items",
        description="Retrieve all items in the user's cart, along with total price.",
        responses={
            200: CartSerializer,
            401: {"detail": "Authentication credentials were not provided."},
        },
    )
    def list(self, request):
        redis_items = CartService.get_all_items(request.user.id)
        products = Product.objects.filter(id__in=redis_items.keys())

        items_data = []
        total_amount = Decimal("0")  # keep it decimal internally
        for p in products:
            qty = int(redis_items[str(p.id)])
            price = get_active_price(p)  # fetch from inventory
            items_data.append(
                {
                    "product_id": p.id,
                    "product_name": p.name,
                    "quantity": qty,
                    "product_price": str(price),  # or you can keep it numeric
                }
            )
            total_amount += price * qty

        # If your test specifically expects total_amount == "0", convert to string
        data = {
            "items": items_data,
            "total_amount": str(total_amount),  # convert to string if test expects "0"
        }
        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Add an item to the cart",
        description="Add a product to the user's cart by providing product ID and quantity.",
        parameters=[
            OpenApiParameter(
                name="product_id",
                type=int,
                required=True,
                description="ID of the product to add",
            ),
            OpenApiParameter(
                name="quantity",
                type=int,
                required=False,
                description="Quantity of the product to add (default is 1)",
            ),
        ],
        responses={
            200: {"detail": "Item added to cart"},
            400: {"detail": "Validation errors"},
        },
    )
    @action(detail=False, methods=["post"], url_path="add-item", url_name="add-item")
    def add_item(self, request):
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity", 1)

        # Validation
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

        # Add item to Redis
        CartService.add_item(request.user.id, product_id, quantity)
        return Response({"detail": "Item added to cart"}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Remove an item from the cart",
        description="Remove a product from the user's cart by providing product ID.",
        parameters=[
            OpenApiParameter(
                name="product_id",
                type=int,
                required=True,
                description="ID of the product to remove",
            ),
        ],
        responses={
            200: {"detail": "Item removed from cart"},
            400: {"detail": "Validation errors"},
        },
    )
    @action(
        detail=False, methods=["post"], url_path="remove-item", url_name="remove-item"
    )
    def remove_item(self, request):
        product_id = request.data.get("product_id")

        # Validation
        if not product_id:
            return Response(
                {"detail": "product_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Remove item from Redis
        CartService.remove_item(request.user.id, product_id)
        return Response({"detail": "Item removed from cart"}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update item quantity in the cart",
        description="Update the quantity of a specific product in the user's cart.",
        parameters=[
            OpenApiParameter(
                name="product_id",
                type=int,
                required=True,
                description="ID of the product to update",
            ),
            OpenApiParameter(
                name="quantity",
                type=int,
                required=True,
                description="New quantity of the product",
            ),
        ],
        responses={
            200: {"detail": "Item quantity updated"},
            400: {"detail": "Validation errors"},
        },
    )
    @action(
        detail=False, methods=["post"], url_path="update-item", url_name="update-item"
    )
    def update_item(self, request):
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity")

        # Validation
        if not product_id or quantity is None:
            return Response(
                {"detail": "product_id and quantity are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            quantity = int(quantity)
        except ValueError:
            return Response(
                {"detail": "quantity must be an integer"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update quantity in Redis
        CartService.set_item_quantity(request.user.id, product_id, quantity)
        return Response({"detail": "Item quantity updated"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="checkout", url_name="checkout")
    def checkout(self, request):
        redis_items = CartService.get_all_items(request.user.id)
        if not redis_items:
            return Response(
                {"detail": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST
            )

        products = Product.objects.filter(id__in=redis_items.keys())

        with transaction.atomic():
            cart = Cart.objects.create(user=request.user, status=CartStatus.CHECKOUT)
            total_amount = Decimal("0")
            for p in products:
                qty = int(redis_items[str(p.id)])
                price = get_active_price(p)  # fetch from inventory
                CartItem.objects.create(cart=cart, product=p, quantity=qty, price=price)
                total_amount += price * qty

            cart.total_amount = total_amount
            cart.status = CartStatus.COMPLETED
            cart.save()

        # Clear Redis
        CartService.clear_cart(request.user.id)

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)
