from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from products.models import Product

from .models import Cart, CartItem, CartStatus
from .serializers import CartSerializer
from .services import CartService


class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        # Display the user's current cart from Redis
        redis_items = CartService.get_all_items(request.user.id)
        products = Product.objects.filter(id__in=redis_items.keys())

        items_data = []
        total_amount = 0
        for p in products:
            qty = int(redis_items[str(p.id)])
            price = p.price  # Assuming the Product model has a price field
            items_data.append(
                {
                    "id": None,
                    "product_id": p.id,
                    "product_name": p.name,
                    "quantity": qty,
                    "product_price": price,
                }
            )
            total_amount += price * qty

        data = {
            "id": None,
            "status": CartStatus.ACTIVE,
            "items": items_data,
            "total_amount": total_amount,
            "created_at": None,
            "updated_at": None,
        }
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def add_item(self, request):
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))
        if not product_id:
            return Response(
                {"detail": "product_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Product review
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND
            )

        CartService.add_item(request.user.id, product_id, quantity)
        return Response({"detail": "Item added to cart"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def remove_item(self, request):
        product_id = request.data.get("product_id")
        if not product_id:
            return Response(
                {"detail": "product_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        CartService.remove_item(request.user.id, product_id)
        return Response({"detail": "Item removed from cart"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def update_item(self, request):
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity")
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

    @action(detail=False, methods=["post"])
    def checkout(self, request):
        # In the Checkout phase, we transfer data from Redis to PostgreSQL
        redis_items = CartService.get_all_items(request.user.id)
        if not redis_items:
            return Response(
                {"detail": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST
            )

        products = Product.objects.filter(id__in=redis_items.keys())

        with transaction.atomic():
            cart = Cart.objects.create(user=request.user, status=CartStatus.CHECKOUT)
            total_amount = 0
            for p in products:
                qty = int(redis_items[str(p.id)])
                price = p.price
                CartItem.objects.create(cart=cart, product=p, quantity=qty, price=price)
                total_amount += price * qty
            cart.total_amount = total_amount
            cart.status = CartStatus.COMPLETED
            cart.save()

        # Clear Redis
        CartService.clear_cart(request.user.id)

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)
