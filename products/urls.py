from django.urls import path

from .views import (
    ProductAttributeDetailView,
    ProductAttributeListView,
    ProductAttributeValueListView,
    ProductDetailView,
    ProductInventoryListView,
    ProductListView,
    ProductMediaListView,
    ProductTypeDetailView,
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
    path(
        "product-types/<int:pk>/",
        ProductTypeDetailView.as_view(),
        name="product-type-detail",
    ),
    path(
        "attributes/", ProductAttributeListView.as_view(), name="product-attribute-list"
    ),
    path(
        "attributes/<int:pk>/",
        ProductAttributeDetailView.as_view(),
        name="product-attribute-detail",
    ),
    path(
        "attributes/<int:attribute_id>/values/",
        ProductAttributeValueListView.as_view(),
        name="product-attribute-value-list",
    ),
]
