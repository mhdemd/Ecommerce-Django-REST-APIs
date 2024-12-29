from django.shortcuts import get_object_or_404
from rest_framework import generics

from .models import Order, OrderItem
from .serializers import OrderItemSerializer, OrderSerializer


# View for listing and creating orders
class OrderListView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        # Only return orders for the authenticated user
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically associate the order with the authenticated user
        serializer.save(user=self.request.user)


# View for retrieving, updating, and deleting a specific order
class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        # Ensure only the owner can access the order
        return Order.objects.filter(user=self.request.user)


# View for listing and creating order items
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
