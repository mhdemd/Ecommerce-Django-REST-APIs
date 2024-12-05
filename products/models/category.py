from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey


class Category(MPTTModel):
    name = models.CharField(
        max_length=100,
        verbose_name=_("Category Name"),
        help_text=_("Required, max 100 characters"),
        unique=True,
        null=False,
        blank=False,
    )
    slug = models.SlugField(
        max_length=150,
        verbose_name=_("Category Safe URL"),
        help_text=_("Required, letters, numbers, underscore, or hyphens"),
        unique=False,
        null=False,
        blank=False,
    )
    is_active = models.BooleanField(default=True)

    parent = TreeForeignKey(
        "self",
        on_delete=models.PROTECT,
        related_name="children",
        verbose_name=_("Parent of Category"),
        help_text=_("Not required"),
        unique=False,
        null=True,
        blank=True,
    )

    class MPTTMeta:
        order_insertion_by = ["name"]

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
        ]
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def get_absolute_url(self):
        return reverse("shop:product_list_by_category", args=[self.slug])

    def __str__(self):
        return self.name
