from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from .models import Order, OrderItem
from .serializers import OrderItemSerializer, OrderSerializer

# ---------------------------------------------------------
# User Endpoints (orders)
# ---------------------------------------------------------


@extend_schema(tags=["Order - List"])
class OrderListView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        # Only return orders for the authenticated user
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically associate the order with the authenticated user
        serializer.save(user=self.request.user)


@extend_schema(tags=["Order - Detail"])
class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        # Ensure only the owner can access the order
        return Order.objects.filter(user=self.request.user)


@extend_schema(tags=["Order - Items"])
class OrderItemListView(generics.ListCreateAPIView):
    serializer_class = OrderItemSerializer

    def get_queryset(self):
        # Get the order and ensure it belongs to the authenticated user
        order_id = self.kwargs.get("order_id")
        order = get_object_or_404(Order, id=order_id, user=self.request.user)
        return OrderItem.objects.filter(order=order)

    def perform_create(self, serializer):
        # Automatically associate the item with the correct order
        order_id = self.kwargs.get("order_id")
        order = get_object_or_404(Order, id=order_id, user=self.request.user)
        serializer.save(order=order)


@extend_schema(tags=["Order - Item Detail"])
class OrderItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderItemSerializer

    def get_queryset(self):
        # Ensure the item belongs to the correct order and user
        order_id = self.kwargs.get("order_id")
        order = get_object_or_404(Order, id=order_id, user=self.request.user)
        return OrderItem.objects.filter(order=order)


# ---------------------------------------------------------
# Admin Endpoints (orders)
# ---------------------------------------------------------


@extend_schema(tags=["Admin - Order"])
class AdminOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [IsAdminUser]
