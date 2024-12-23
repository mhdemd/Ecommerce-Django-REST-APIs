from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Comment, Review, ReviewVote
from .serializers import CommentSerializer, ReviewSerializer, ReviewVoteSerializer


# ----------------------
# Views for Regular Users
# ----------------------
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


class CommentListView(generics.ListAPIView):
    """
    List all comments for a specific review
    """

    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        review_id = self.kwargs.get("review_id")
        return Comment.objects.filter(review_id=review_id)


# ----------------------
# Views for Admins
# ----------------------
class AdminReviewListView(generics.ListAPIView):
    """
    List all reviews for moderation
    """

    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return Review.objects.all()


class AdminReviewApprovalView(APIView):
    """
    Approve or reject a review
    """

    permission_classes = [permissions.IsAdminUser]

    def post(self, request, review_id):
        review = Review.objects.get(id=review_id)
        is_approved = request.data.get("is_approved", False)
        review.is_approved = is_approved
        review.save()
        return Response(
            {"success": f"Review {'approved' if is_approved else 'rejected'}"},
            status=status.HTTP_200_OK,
        )
