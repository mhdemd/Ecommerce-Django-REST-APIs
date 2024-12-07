from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # API schema and docs
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # Admin and Authentication
    path("admin/", admin.site.urls),
    path("auth/", include("authentication.urls")),
    # Applications
    path("products/", include("products.urls")),
    # path("brands/", include("brands.urls")),
    # path("categories/", include("categories.urls")),
    # path("wishlist/", include("wishlist.urls")),
    # path("reviews/", include("reviews.urls")),
]
