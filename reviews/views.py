from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from drf_spectacular.views import SpectacularAPIView
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product

from .models import Comment, Review, ReviewVote
from .serializers import CommentSerializer, ReviewSerializer, ReviewVoteSerializer

# ---------------------------- Create schema for swagger ----------------------------
reviews_schema_view = SpectacularAPIView.as_view(urlconf="reviews.urls")


# ----------------------
# Views for Regular Users
# ----------------------


@extend_schema(tags=["Review - List"])
class ReviewListView(generics.ListAPIView):
    """
    List all approved reviews for a specific product
    """

    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        product_id = self.kwargs.get("product_id")
        return Review.objects.filter(
            product_id=product_id, is_approved=True
        ).select_related("user", "product")


@extend_schema(tags=["Review - Create"])
class ReviewCreateView(generics.CreateAPIView):
    """
    Create a new review for a product
    """

    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        product_id = self.kwargs.get("product_id")
        product = get_object_or_404(Product, id=product_id)
        serializer.save(user=self.request.user, product=product)


@extend_schema(tags=["Review - Update/Delete"])
class ReviewUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    Update or delete a review (only allowed for the review's author)
    """

    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)


@extend_schema(tags=["Review - Vote"])
class ReviewVoteView(APIView):
    """
    Like or dislike a review
    """

    serializer_class = ReviewVoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, review_id):
        """
        Handles creating or updating a vote for a review
        """
        review = get_object_or_404(Review, id=review_id)
        data = {
            "review": review.id,
            "is_upvote": request.data.get("is_upvote"),
        }
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            vote, created = ReviewVote.objects.update_or_create(
                user=request.user,
                review=review,
                defaults={"is_upvote": serializer.validated_data["is_upvote"]},
            )
            message = "Vote created" if created else "Vote updated"
            return Response(
                {"success": message, "data": self.serializer_class(vote).data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Review - Comment"])
class CommentCreateView(generics.CreateAPIView):
    """
    Add a comment to a review
    """

    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        review_id = self.kwargs.get("review_id")
        review = get_object_or_404(Review, id=review_id)
        serializer.save(user=self.request.user, review=review)


@extend_schema(tags=["Review - Comment"])
class CommentListView(generics.ListAPIView):
    """
    List all comments for a specific review
    """

    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        review_id = self.kwargs.get("review_id")
        return Comment.objects.filter(review_id=review_id).select_related(
            "user", "review"
        )


# ----------------------
# Views for Admins
# ----------------------


@extend_schema(tags=["Admin - Review"])
class AdminReviewListView(generics.ListAPIView):
    """
    List all reviews for moderation
    """

    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return Review.objects.all().select_related("user", "product")


@extend_schema(tags=["Admin - Review"])
class AdminReviewApprovalView(APIView):
    """
    Approve or reject a review
    """

    permission_classes = [permissions.IsAdminUser]

    def post(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)
        is_approved = request.data.get("is_approved")
        if not isinstance(is_approved, bool):
            return Response(
                {"error": "Invalid value for 'is_approved'. Must be true or false."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        review.is_approved = is_approved
        review.save()
        return Response(
            {"success": f"Review {'approved' if is_approved else 'rejected'}"},
            status=status.HTTP_200_OK,
        )
