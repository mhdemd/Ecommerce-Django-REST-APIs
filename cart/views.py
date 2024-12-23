from decimal import Decimal

from django.db import transaction
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from drf_spectacular.views import SpectacularAPIView
from rest_framework import status
from rest_framework.generics import GenericAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from cart.models import Cart, CartItem, CartStatus
from cart.serializers import CartSerializer
from cart.services import CartService
from products.models import Product

from .services import get_active_price

# ---------------------------- Create schema for swagger ----------------------------
cart_schema_view = SpectacularAPIView.as_view(urlconf="cart.urls")


# -------------------------
# User Endpoints
# -------------------------
@extend_schema_view(
    get=extend_schema(
        tags=["Cart - Management"],
        summary="Get current user's cart items",
        description="Retrieve all items in the user's cart, along with total price.",
        responses={200: CartSerializer},
    )
)
class CartListView(GenericAPIView):
    permission_classes = [IsAuthenticated]

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


@extend_schema_view(
    post=extend_schema(
        tags=["Cart - Management"],
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
                description="Quantity to add (default is 1)",
            ),
        ],
        responses={
            200: {"detail": "Item added to cart"},
            400: {"detail": "Validation errors"},
        },
    )
)
class CartAddItemView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Check both request.data and query parameters for product_id
        product_id = request.data.get("product_id") or request.query_params.get(
            "product_id"
        )
        quantity = request.data.get("quantity") or request.query_params.get(
            "quantity", 1
        )

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


@extend_schema_view(
    post=extend_schema(
        tags=["Cart - Management"],
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
)
class CartRemoveItemView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get("product_id") or request.query_params.get(
            "product_id"
        )

        if not product_id:
            return Response(
                {"detail": "product_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        CartService.remove_item(request.user.id, product_id)
        return Response({"detail": "Item removed from cart"}, status=status.HTTP_200_OK)


@extend_schema_view(
    post=extend_schema(
        tags=["Cart - Management"],
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
)
class CartUpdateItemView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get("product_id") or request.query_params.get(
            "product_id"
        )
        quantity = request.data.get("quantity") or request.query_params.get("quantity")

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

        CartService.set_item_quantity(request.user.id, product_id, quantity)
        return Response({"detail": "Item quantity updated"}, status=status.HTTP_200_OK)


@extend_schema_view(
    post=extend_schema(
        tags=["Cart - Checkout"],
        summary="Checkout the cart",
        description="Complete the checkout process for the current user's cart.",
        responses={200: CartSerializer, 400: {"detail": "Cart is empty"}},
    )
)
class CartCheckoutView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
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
                price = get_active_price(p)
                CartItem.objects.create(cart=cart, product=p, quantity=qty, price=price)
                total_amount += price * qty

            cart.total_amount = total_amount
            cart.status = CartStatus.COMPLETED
            cart.save()

        CartService.clear_cart(request.user.id)
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)


# -------------------------
# Admin Endpoints
# -------------------------
@extend_schema_view(
    get=extend_schema(
        tags=["Admin - Cart"],
        summary="List all user carts",
        description="Retrieve a list of all user carts, including details about their status and total amount.",
    )
)
class AdminCartListView(ListAPIView):
    queryset = Cart.objects.all().order_by("-created_at")
    serializer_class = CartSerializer
    permission_classes = [IsAdminUser]


@extend_schema_view(
    get=extend_schema(
        tags=["Admin - Cart"],
        summary="Retrieve details of a specific cart",
        description="Retrieve detailed information about a specific user's cart, including items and total amount.",
    )
)
class AdminCartDetailView(RetrieveAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAdminUser]
