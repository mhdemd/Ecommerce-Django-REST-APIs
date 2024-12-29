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
