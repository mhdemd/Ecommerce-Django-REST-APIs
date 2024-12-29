from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics

from .models import Order, OrderItem
from .serializers import OrderItemSerializer, OrderSerializer


@extend_schema(
    summary="List and Create Orders",
    description="Retrieve a list of orders for the authenticated user or create a new order.",
    responses={200: OrderSerializer, 201: OrderSerializer},
)
class OrderListView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        # Only return orders for the authenticated user
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically associate the order with the authenticated user
        serializer.save(user=self.request.user)


@extend_schema(
    summary="Retrieve, Update, or Delete an Order",
    description="Retrieve, update, or delete a specific order for the authenticated user.",
    responses={200: OrderSerializer},
)
class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        # Ensure only the owner can access the order
        return Order.objects.filter(user=self.request.user)


@extend_schema(
    summary="List and Create Order Items",
    description="Retrieve a list of items for a specific order or add a new item to the order.",
    parameters=[
        OpenApiParameter("order_id", int, description="ID of the order"),
    ],
    responses={200: OrderItemSerializer, 201: OrderItemSerializer},
)
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


@extend_schema(
    summary="Retrieve, Update, or Delete an Order Item",
    description="Retrieve, update, or delete a specific item within an order.",
    parameters=[
        OpenApiParameter("order_id", int, description="ID of the order"),
        OpenApiParameter("pk", int, description="ID of the order item"),
    ],
    responses={200: OrderItemSerializer},
)
class OrderItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderItemSerializer

    def get_queryset(self):
        # Ensure the item belongs to the correct order and user
        order_id = self.kwargs.get("order_id")
        order = get_object_or_404(Order, id=order_id, user=self.request.user)
        return OrderItem.objects.filter(order=order)
