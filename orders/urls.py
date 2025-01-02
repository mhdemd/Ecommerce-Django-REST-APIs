from django.urls import path

from .views import (
    AdminOrderListView,
    OrderDetailView,
    OrderItemDetailView,
    OrderItemListView,
    OrderListView,
    orders_schema_view,
)

urlpatterns = [
    # ---------------------------------------------------------
    # User Endpoints (orders)
    # ---------------------------------------------------------
    path("", OrderListView.as_view(), name="order-list"),
    path("<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path(
        "<int:order_id>/items/",
        OrderItemListView.as_view(),
        name="order-item-list",
    ),
    path(
        "<int:order_id>/items/<int:pk>/",
        OrderItemDetailView.as_view(),
        name="order-item-detail",
    ),
    # ---------------------------------------------------------
    # Admin Endpoints (orders)
    # ---------------------------------------------------------
    path("admin/", AdminOrderListView.as_view(), name="admin-order-list"),
    # Create schema for swagger
    path("schema/", orders_schema_view, name="auth-schema"),
]
