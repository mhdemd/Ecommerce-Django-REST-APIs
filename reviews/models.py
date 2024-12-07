from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from products.models.product import Product


class ProductReview(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("User"),
        help_text=_("The user who wrote the review."),
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name=_("Product"),
        help_text=_("The product that this review is for."),
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_("Review Title"),
        help_text=_("Optional, max 255 characters"),
        null=True,
        blank=True,
    )
    review = models.TextField(
        verbose_name=_("Review Content"),
        help_text=_("Required. The content of the review."),
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("Rating"),
        help_text=_("Required. An integer between 1 and 5."),
    )
    date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Date Created"),
        help_text=_("The date and time when the review was created."),
    )
    show_name = models.BooleanField(
        default=True,
        verbose_name=_("Show Name"),
        help_text=_("If checked, the user's name will be displayed."),
    )
    is_approved = models.BooleanField(
        default=False,
        verbose_name=_("Is Approved"),
        help_text=_("Designates whether the review is approved by an admin."),
    )

    class Meta:
        verbose_name = _("Product Review")
        verbose_name_plural = _("Product Reviews")
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["product"]),
            models.Index(fields=["user"]),
            models.Index(fields=["is_approved"]),
        ]

    def __str__(self):
        user_name = self.user.get_full_name() if self.user else "Anonymous"
        return f"Review for {self.product.name} by {user_name}"

    def get_absolute_url(self):
        return reverse("review_detail", args=[str(self.id)])

    def get_rating(self):
        return self.rating
