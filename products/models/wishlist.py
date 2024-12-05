from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from product import Product


class Wishlist(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("User"),
        help_text=_("The user who added the product to the wishlist."),
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name=_("Product"),
        help_text=_("The product added to the wishlist."),
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Date Added"),
        help_text=_("The date and time when the product was added to the wishlist."),
    )

    class Meta:
        unique_together = ("user", "product")
        verbose_name = _("Wishlist Item")
        verbose_name_plural = _("Wishlist Items")
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["product"]),
        ]

    def __str__(self):
        return f"{self.user.username}'s wishlist item: {self.product.name}"
