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


class ReviewCreateView(generics.CreateAPIView):
    """
    Create a new review for a product
    """

    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReviewUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    Update or delete a review (only allowed for the review's author)
    """

    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)


class ReviewVoteView(APIView):
    """
    Like or dislike a review
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, review_id):
        is_upvote = request.data.get("is_upvote")
        review = Review.objects.get(id=review_id)
        vote, created = ReviewVote.objects.get_or_create(
            user=request.user, review=review, defaults={"is_upvote": is_upvote}
        )
        if not created:
            vote.is_upvote = is_upvote
            vote.save()
        return Response({"success": "Vote recorded"}, status=status.HTTP_200_OK)


class CommentCreateView(generics.CreateAPIView):
    """
    Add a comment to a review
    """

    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
