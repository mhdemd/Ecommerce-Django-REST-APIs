from django.urls import path

from .views import (
    AdminReviewApprovalView,
    AdminReviewListView,
    CommentCreateView,
    CommentListView,
    ReviewCreateView,
    ReviewListView,
    ReviewUpdateDeleteView,
    ReviewVoteView,
)

urlpatterns = [
    # ------------------------
    # Regular User Routes
    # ------------------------
    path(
        "products/<int:product_id>/reviews/",
        ReviewListView.as_view(),
        name="review-list",
    ),
    path(
        "products/<int:product_id>/reviews/create/",
        ReviewListView.as_view(),
        name="review-create",
    ),
    path(
        "reviews/<int:pk>/",
        ReviewUpdateDeleteView.as_view(),
        name="review-detail",
    ),
    path(
        "reviews/<int:review_id>/comments/",
        CommentListView.as_view(),
        name="comment-list",
    ),
    path(
        "reviews/<int:review_id>/comments/create/",
        CommentCreateView.as_view(),
        name="comment-create",
    ),    ),

]
