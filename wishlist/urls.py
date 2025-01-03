from django.urls import path

from .views import WishlistDetailView, WishlistListCreateView

urlpatterns = [
    path("", WishlistListCreateView.as_view(), name="wishlist-list-create"),
    path("<int:pk>/", WishlistDetailView.as_view(), name="wishlist-detail"),
]
