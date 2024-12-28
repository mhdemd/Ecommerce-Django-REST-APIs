import json

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from products.models.product import Product
from reviews.models import Comment, Review, ReviewVote

User = get_user_model()


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
def comment(user, review):
    """Creates a comment for a review by a user."""
    return Comment.objects.create(user=user, review=review, body="Nice review!")


@pytest.fixture
def another_product(db, brand, category_active):
    """Creates a different product."""
    return Product.objects.create(
        web_id="56789",
        slug="test-product-2",
        name="Test Product 2",
        description="Another test product",
        brand=brand,
        category=category_active,  # Use category_active here
        is_active=True,
    )


@pytest.fixture
def another_user(db):
    """Creates another user."""
    return User.objects.create_user(
        username="another_user", email="another@example.com", password="testpassword"
    )


@pytest.fixture
def review_unapproved(db, another_user, another_product):
    """Creates an unapproved review for a different product."""
    return Review.objects.create(
        user=another_user,
        product=another_product,
        title="Pending Review",
        body="Need approval",
        rating=4,
        is_approved=False,
    )


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


@pytest.mark.django_db
def test_update_review(authenticated_user_client, review):
    """Test update an existing review."""
    url = reverse("review-detail", kwargs={"pk": review.id})
    payload = {"title": "Update Title"}
    response = authenticated_user_client.patch(url, payload)
    assert response.status_code == status.HTTP_200_OK
    review.refresh_from_db()
    assert review.title == "Update Title"


@pytest.mark.django_db
def test_delete_review(authenticated_user_client, review):
    """Test deleting an existing review."""
    url = reverse("review-detail", kwargs={"pk": review.id})
    response = authenticated_user_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Review.objects.filter(id=review.id).exists()


@pytest.mark.django_db
def test_vote_review(authenticated_user_client, review):
    """Test updating a review."""
    url = reverse("review-vote", kwargs={"review_id": review.id})
    payload = {"is_upvote": True}
    response = authenticated_user_client.post(url, payload)
    assert response.status_code == status.HTTP_200_OK
    assert ReviewVote.objects.filter(
        review=review, user=review.user, is_upvote=True
    ).exists()


# ------------------------
# Test Cases for Comments
# ------------------------


@pytest.mark.django_db
def test_list_comments(api_client, review, comment):
    """Test listing comments for a specific reviwe."""
    url = reverse("comment-list", kwargs={"review_id": review.id})
    response = api_client.get(url)
    print(response.data)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["body"] == "Nice review!"


@pytest.mark.django_db
def test_create_comment(authenticated_user_client, review):
    """Test creating a comment for a review."""
    url = reverse("comment-create", kwargs={"review_id": review.id})
    payload = {"body": "I agree with this review!"}
    response = authenticated_user_client.post(url, payload)
    print(response.data)
    assert response.status_code == status.HTTP_201_CREATED
    assert Comment.objects.filter(
        body="I agree with this review!", review=review
    ).exists()


# ---------------------------------
# Test Cases for Admin Views
# ---------------------------------


@pytest.mark.django_db
def test_admin_list_reviews(authenticated_admin_client, review, review_unapproved):
    """Test admin listing all reviews for moderation."""
    url = reverse("admin-review-list")
    response = authenticated_admin_client.get(url)
    print(response.data)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2  # Assuming pagination in response


@pytest.mark.django_db
def test_admin_approve_review(authenticated_admin_client, review_unapproved):
    """Test admin approving a review."""
    url = reverse("admin-review-approve", kwargs={"review_id": review_unapproved.id})
    payload = {"is_approved": True}
    response = authenticated_admin_client.post(
        url, data=json.dumps(payload), content_type="application/json"  # Use json.dumps
    )
    print(response.data)
    assert response.status_code == status.HTTP_200_OK
    review_unapproved.refresh_from_db()
    assert review_unapproved.is_approved is True
