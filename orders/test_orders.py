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

    # ---------------------------------
    # Admin Endpoints
    # ---------------------------------

    def test_list_orders_admin(self, authenticated_admin_client, user, admin_user):
        """Test listing all orders for an admin."""
        url = reverse("admin-order-list")
        Order.objects.bulk_create(
            [
                Order(user=user, total_amount=100),
                Order(user=admin_user, total_amount=200),
            ]
        )

        response = authenticated_admin_client.get(url)

        assert response.status_code == 200
        assert response.data["count"] == 2  # تعداد کل سفارش‌ها
        assert len(response.data["results"]) == 2  # تعداد آیتم‌های در صفحه

    def test_list_orders_non_admin(self, authenticated_user_client):
        """Test listing orders for a non-admin user."""
        url = reverse("admin-order-list")

        response = authenticated_user_client.get(url)

        assert response.status_code == 403  # Forbidden for non-admins

    # ---------------------------------
    # Order Items
    # ---------------------------------

    def test_list_order_items(self, authenticated_user_client, user, product):
        """Test listing items of a specific order."""
        order = Order.objects.create(user=user, total_amount=100)
        OrderItem.objects.create(order=order, product=product, quantity=2, price=50)

        url = reverse("order-item-list", kwargs={"order_id": order.id})
        response = authenticated_user_client.get(url)

        assert response.status_code == 200
        assert response.data["count"] == 1
        assert len(response.data["results"]) == 1

    def test_create_order_item(self, authenticated_user_client, user, product):
        """Test creating an item for a specific order."""
        order = Order.objects.create(user=user, total_amount=100)
        url = reverse("order-item-list", kwargs={"order_id": order.id})

        payload = {"product": product.id, "quantity": 1, "price": 30}
        response = authenticated_user_client.post(url, payload)

        assert response.status_code == 201
        assert response.data["quantity"] == 1
        assert response.data["price"] == "30.00"

    def test_update_order_item(self, authenticated_user_client, user, product):
        """Test updating an order item."""
        order = Order.objects.create(user=user, total_amount=100)
        item = OrderItem.objects.create(
            order=order, product=product, quantity=1, price=20
        )

        url = reverse("order-item-detail", kwargs={"order_id": order.id, "pk": item.id})
        payload = {"quantity": 3}
        response = authenticated_user_client.patch(url, payload)

        assert response.status_code == 200
        assert response.data["quantity"] == 3

    def test_delete_order_item(self, authenticated_user_client, user, product):
        """Test deleting an order item."""
        order = Order.objects.create(user=user, total_amount=100)
        item = OrderItem.objects.create(
            order=order, product=product, quantity=1, price=20
        )

        url = reverse("order-item-detail", kwargs={"order_id": order.id, "pk": item.id})
        response = authenticated_user_client.delete(url)

        assert response.status_code == 204
        assert not OrderItem.objects.filter(id=item.id).exists()
