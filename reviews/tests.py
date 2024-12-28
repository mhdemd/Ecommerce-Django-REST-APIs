import pytest
from django.urls import reverse
from rest_framework import status

from reviews.models import Comment, Review, ReviewVote


# ------------------------
# Review Test Fixtures
# ------------------------
@pytest.fixture
def review(user, product):
    """Create a review for a product by a user."""
    return Review.objects.create(
        user=user,
        product=product,
        title="Great Product",
        body="Love it!",
        rating=5,
        is_approved=True,
    )


@pytest.fixture
def review_unapproved(user, product):
    """Create an unapproved review for a product by a user."""
    return Review.objects.create(
        user=user,
        product=product,
        title="Pending Review",
        body="Need approval",
        rating=4,
        is_approved=False,
    )
