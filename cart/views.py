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
