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


@pytest.fixture
def Comment(user, review):
    """Create a comment for a review by a user."""
    return Comment.objects.create(user=user, review=review, body="Nice review!")


# ------------------------
# Test Cases for Reviews
# ------------------------
@pytest.mark.django_db
def test_list_approved_reviews(api_client, product, review):
    """Test listing approved reviews for a product."""
    url = reverse("review-list", kwargs={"product_id": product.id})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["title"] == "Great Product"


@pytest.mark.django_db
def test_create_review(authenticated_user_client, product):
    """Test creating a new review for a product."""
    url = reverse("review-create", kwargs={"product_id": product.id})
    payload = {"title": "Amazing!", "body": "Very satisfied!", "rating": 5}
    response = authenticated_user_client.post(url, payload)
    print(response.data)

    assert response.status_code == status.HTTP_201_CREATED
    assert Review.objects.filter(title="Amazing!", product=product).exists()
