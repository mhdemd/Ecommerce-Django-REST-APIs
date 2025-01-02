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
