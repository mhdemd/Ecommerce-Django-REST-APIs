from django.urls import path

from .views import (
    OrderDetailView,
    OrderItemDetailView,
    OrderItemListView,
    OrderListView,
)

urlpatterns = [
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
]
