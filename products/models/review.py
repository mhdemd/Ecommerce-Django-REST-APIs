from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey


class ProductReview(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_("Review Title"),
        help_text=_("Optional, max 255 characters"),
        null=True,
        blank=True,
    )
    review = models.TextField()
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    date = models.DateTimeField(auto_now_add=True)
    show_name = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = _("Product Reviews")
        ordering = ["-date"]

    def __str__(self):
        return f"Review for {self.product.name} by {self.user}"

    def get_rating(self):
        return self.rating
