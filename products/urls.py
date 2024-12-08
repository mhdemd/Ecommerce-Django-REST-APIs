from django.urls import path

from .views import (
    AdminProductDetailView,
    AdminProductInventoryListCreateView,
    AdminProductListCreateView,
    AdminProductMediaDetailView,
    AdminProductMediaListCreateView,
    ProductAttributeDetailView,
    ProductAttributeListView,
    ProductAttributeValueDetailView,
    ProductAttributeValueListView,
    ProductDetailView,
    ProductInventoryListView,
    ProductListView,
    ProductMediaListView,
    ProductTypeDetailView,
    ProductTypeListView,
)

urlpatterns = [
    # User Endpoints (Products)
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
    path(
        "attributes/<int:attribute_id>/values/<int:value_id>/",
        ProductAttributeValueDetailView.as_view(),
        name="product-attribute-value-detail",
    ),
    # Admin Endpoints (Products)
    path(
        "admin/products/",
        AdminProductListCreateView.as_view(),
        name="admin-product-list-create",
    ),
    path(
        "admin/products/<int:pk>/",
        AdminProductDetailView.as_view(),
        name="admin-product-detail",
    ),
    path(
        "admin/products/<int:id>/media/",
        AdminProductMediaListCreateView.as_view(),
        name="admin-product-media-list-create",
    ),
    path(
        "admin/products/<int:product_id>/media/<int:pk>/",
        AdminProductMediaDetailView.as_view(),
        name="admin-product-media-detail",
    ),
    path(
        "admin/inventories/",
        AdminProductInventoryListCreateView.as_view(),
        name="admin-product-inventory-list-create",
    ),
]
