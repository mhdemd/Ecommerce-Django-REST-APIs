from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from products.models import Product

from .models import Cart, CartItem, CartStatus
from .serializers import CartItemSerializer, CartSerializer
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
