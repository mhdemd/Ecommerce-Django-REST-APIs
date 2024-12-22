from django.urls import path

from .views import (
    CartAddItemView,
    CartCheckoutView,
    CartListView,
    CartRemoveItemView,
    CartUpdateItemView,
)

urlpatterns = [
    path("", CartListView.as_view(), name="cart-list"),
    path("add-item/", CartAddItemView.as_view(), name="cart-add-item"),
    path("remove-item/", CartRemoveItemView.as_view(), name="cart-remove-item"),
    path("update-item/", CartUpdateItemView.as_view(), name="cart-update-item"),
    path("checkout/", CartCheckoutView.as_view(), name="cart-checkout"),
]
