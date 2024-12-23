from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from products.models import Product


class CartStatus(models.TextChoices):
    ACTIVE = "active", _("Active")
    CHECKOUT = "checkout", _("Checkout")
    COMPLETED = "completed", _("Completed")
    CANCELED = "canceled", _("Canceled")


class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="carts"
    )
    status = models.CharField(
        max_length=20, choices=CartStatus.choices, default=CartStatus.ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    # The final amount may be calculated and saved at the Checkout stage
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Cart {self.pk} - {self.user.email} - {self.status}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ("cart", "product")

    def __str__(self):
        return f"{self.product.name} x {self.quantity} in Cart {self.cart_id}"
