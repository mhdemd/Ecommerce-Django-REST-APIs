from django.urls import path

from .views import (
    AdminBrandDetailView,
    AdminBrandListCreateView,
    BrandDetailView,
    BrandListView,
)

urlpatterns = [
    # User Endpoints (Brands)
    path("brands/", BrandListView.as_view(), name="brand-list"),
    path("brands/<int:pk>/", BrandDetailView.as_view(), name="brand-detail"),
    # Admin Endpoints (Brands)
    path(
        "admin/brands/",
        AdminBrandListCreateView.as_view(),
        name="admin-brand-list-create",
    ),
    path(
        "admin/brands/<int:pk>/",
        AdminBrandDetailView.as_view(),
        name="admin-brand-detail",
    ),
]
