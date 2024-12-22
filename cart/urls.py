from django.urls import path

from .views import CartViewSet

urlpatterns = [
    # GET: List of items in the shopping cart
    path("", CartViewSet.as_view({"get": "list"}), name="cart-list"),
    # POST: Add item to cart
    path(
        "add-item/",
        CartViewSet.as_view({"post": "add_item"}),
        name="cart-add-item",
    ),
    # POST: Remove item from cart
    path(
        "remove-item/",
        CartViewSet.as_view({"post": "remove_item"}),
        name="cart-remove-item",
    ),
    # POST: Update the quantity of an item
    path(
        "update-item/",
        CartViewSet.as_view({"post": "update_item"}),
        name="cart-update-item",
    ),
    # POST: Shopping cart checkout
    path(
        "checkout/",
        CartViewSet.as_view({"post": "checkout"}),
        name="cart-checkout",
    ),
]
