from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
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
        null=False,
        blank=False,
    )

    def __str__(self):
        return self.name


class ProductAttribute(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name=_("Product Attribute Name"),
        help_text=_("Required, unique, max 255 characters"),
        unique=True,
        null=False,
        blank=False,
    )
    description = models.TextField(
        verbose_name=_("Product Attribute Description"),
        help_text=_("Required"),
        unique=False,
        null=False,
        blank=False,
    )

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
        unique=False,
        null=False,
        blank=False,
    )

    def __str__(self):
        return f"{self.product_attribute.name}: {self.attribute_value}"
