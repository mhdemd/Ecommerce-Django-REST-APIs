from django.urls import path

from .views import (
    AdminBrandDetailView,
    AdminBrandListCreateView,
    BrandDetailView,
    BrandListView,
)

urlpatterns = [
    # User Endpoints (Brands)
    path("", BrandListView.as_view(), name="brand-list"),
    path("<int:pk>/", BrandDetailView.as_view(), name="brand-detail"),
    # Admin Endpoints (Brands)
    path(
        "admin/",
        AdminBrandListCreateView.as_view(),
        name="admin-brand-list-create",
    ),
    path(
        "admin/<int:pk>/",
        AdminBrandDetailView.as_view(),
        name="admin-brand-detail",
    ),
]
