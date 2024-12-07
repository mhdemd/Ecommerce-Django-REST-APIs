from django.urls import path

from .views import ProductDetailView, ProductListView, ProductMediaListView

urlpatterns = [
    path("products/", ProductListView.as_view(), name="product-list"),
    path("<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("<int:pk>/media/", ProductMediaListView.as_view(), name="product-media-list"),
]
