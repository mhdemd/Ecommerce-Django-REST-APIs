from rest_framework import viewsets

from .models import Order
from .serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        # Return orders only for the logged-in user
        user = self.request.user
        if user.is_authenticated:
            return Order.objects.filter(user=user)
        return Order.objects.none()
