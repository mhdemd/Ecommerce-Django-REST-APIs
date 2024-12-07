from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Brand(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("Brand Name"),
        help_text=_("Required, unique, max 255 characters"),
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name=_("Brand Slug"),
        help_text=_("Unique URL identifier for the brand."),
    )
    description = models.TextField(
        verbose_name=_("Brand Description"),
        help_text=_("Optional"),
        null=True,
        blank=True,
    )
    logo = models.ImageField(
        upload_to="brand_logos/",
        verbose_name=_("Brand Logo"),
        help_text=_("Optional"),
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "png", "jpeg"])],
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Date Brand Created"),
        help_text=_("Format: Y-m-d H:M:S"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Date Brand Updated"),
        help_text=_("Format: Y-m-d H:M:S"),
    )

    class Meta:
        verbose_name = _("Brand")
        verbose_name_plural = _("Brands")
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("brand_detail", args=[self.slug])
