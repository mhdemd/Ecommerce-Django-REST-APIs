from django.urls import path

from .views import (
    ProductDetailView,
    ProductInventoryListView,
    ProductListView,
    ProductMediaListView,
    ProductTypeListView,
)

urlpatterns = [
    path("products/", ProductListView.as_view(), name="product-list"),
    path("<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("<int:pk>/media/", ProductMediaListView.as_view(), name="product-media-list"),
    path(
        "<int:pk>/inventory/",
        ProductInventoryListView.as_view(),
        name="product-inventory-list",
    ),
    path("product-types/", ProductTypeListView.as_view(), name="product-type-list"),
]
