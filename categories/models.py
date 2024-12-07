from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey


class Category(MPTTModel):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("Category Name"),
        help_text=_("Required, max 100 characters"),
    )
    slug = models.SlugField(
        max_length=150,
        unique=True,
        verbose_name=_("Category Safe URL"),
        help_text=_("Required, letters, numbers, underscore, or hyphens"),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active"),
        help_text=_("Designates whether this category is active."),
    )
    parent = TreeForeignKey(
        "self",
        on_delete=models.PROTECT,
        related_name="children",
        verbose_name=_("Parent of Category"),
        help_text=_("Not required"),
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Date Category Created"),
        help_text=_("Format: Y-m-d H:M:S"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Date Category Updated"),
        help_text=_("Format: Y-m-d H:M:S"),
    )

    class MPTTMeta:
        order_insertion_by = ["name"]

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["slug"]),
        ]
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        unique_together = ("slug", "parent")

    def get_absolute_url(self):
        return reverse("category_detail", args=[self.slug])

    def __str__(self):
        return self.name
