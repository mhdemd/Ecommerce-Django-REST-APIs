from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey


class ProductType(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name=_("Type of Product"),
        help_text=_("Required, unique, max 255 characters"),
        unique=True,
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name=_("Product Type Slug"),
        help_text=_("Unique URL identifier for product type."),
    )

    class Meta:
        ordering = ["name"]
        verbose_name = _("Product Type")
        verbose_name_plural = _("Product Types")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("product_type_detail", args=[self.slug])


class ProductAttribute(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name=_("Product Attribute Name"),
        help_text=_("Required, unique, max 255 characters"),
        unique=True,
    )
    description = models.TextField(
        verbose_name=_("Product Attribute Description"),
        help_text=_("Optional"),
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = _("Product Attribute")
        verbose_name_plural = _("Product Attributes")

    def __str__(self):
        return self.name


class ProductAttributeValue(models.Model):
    product_attribute = models.ForeignKey(
        ProductAttribute,
        related_name="values",
        on_delete=models.CASCADE,
    )
    attribute_value = models.CharField(
        max_length=255,
        verbose_name=_("Attribute Value"),
        help_text=_("Required, max 255 characters"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]
        unique_together = ("product_attribute", "attribute_value")
        verbose_name = _("Product Attribute Value")
        verbose_name_plural = _("Product Attribute Values")

    def __str__(self):
        return f"{self.product_attribute.name}: {self.attribute_value}"
