from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Comment, Review, ReviewVote
from .serializers import CommentSerializer, ReviewSerializer, ReviewVoteSerializer


class ReviewListView(generics.ListAPIView):
    """
    List all approved reviews for a specific product
    """

    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        product_id = self.kwargs.get("product_id")
        return Review.objects.filter(product_id=product_id, is_approved=True)
