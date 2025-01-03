from rest_framework import generics, permissions

from .models import Wishlist
from .serializers import WishlistSerializer


class WishlistListCreateView(generics.ListCreateAPIView):
    """
    Handles listing and creating wishlist items for the authenticated user.
    """

    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WishlistDetailView(generics.RetrieveDestroyAPIView):
    """
    Handle retrieving and deleting a single wishlist item for the authenticated user.
    """

    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)
