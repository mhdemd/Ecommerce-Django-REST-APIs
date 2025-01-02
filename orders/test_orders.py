import pytest
from django.urls import reverse

from orders.models import Order, OrderItem


@pytest.mark.django_db
class TestOrderEndpoints:
    # --------------------------------
    # User Endpoint
    # --------------------------------

    def test_list_orders_authenticated_user(self, authenticated_user_client, user):
        """Test listing orders for an authenticated user."""
        url = reverse("order-list")
        Order.objects.create(user=user, total_amount=100)

        response = authenticated_user_client.get(url)
        print(response.data)
        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["total_amount"] == "100.00"

    def test_creatd_orders_authenticated_user(self, authenticated_user_client):
        """Test creating an order for an authenticated user."""
        url = reverse("order-list")

        payload = {"status": "pending", "total_amount": 150}
        response = authenticated_user_client.post(url, payload)

        print(response.data)

        assert response.status_code == 201
        assert response.data["total_amount"] == "150.00"
        assert response.data["status"] == "pending"

    def test_retrieve_order_authenticated_user(self, authenticated_user_client, user):
        """Test retrieving a specific order for the authenticated user."""
        order = Order.objects.create(user=user, total_amount=200)
        url = reverse("order-detail", kwargs={"pk": order.id})

        response = authenticated_user_client.get(url)

        assert response.status_code == 200
        assert response.data["total_amount"] == "200.00"

    def test_update_order_authenticated_user(self, authenticated_user_client, user):
        """Test updating an order for the authenticated user."""
        order = Order.objects.create(user=user, total_amount=300)
        url = reverse("order-detail", kwargs={"pk": order.id})

        payload = {"status": "paid"}
        response = authenticated_user_client.patch(url, payload)

        assert response.status_code == 200
        assert response.data["status"] == "paid"

    def test_delete_order_authenticated_user(self, authenticated_user_client, user):
        """Test deleting an order for the authenticated user."""
        order = Order.objects.create(user=user, total_amount=300)
        url = reverse("order-detail", kwargs={"pk": order.id})

        response = authenticated_user_client.delete(url)

        assert response.status_code == 204
        assert not Order.objects.filter(id=order.id).exists()
