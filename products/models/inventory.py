from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey


class ProductInventory(models.Model):
    sku = models.CharField(
        max_length=20,
        verbose_name=_("Stock Keeping Unit (SKU)"),
        help_text=_("Required, unique, max 20 characters"),
        unique=True,
        null=False,
        blank=False,
    )
    upc = models.CharField(
        max_length=12,
        verbose_name=_("Universal Product Code (UPC)"),
        help_text=_("Required, unique, max 12 characters"),
        unique=True,
        null=False,
        blank=False,
    )
    product_type = models.ForeignKey(
        ProductType,
        related_name="product_inventories",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    product = models.ForeignKey(
        Product, related_name="product_inventory", on_delete=models.CASCADE
    )
    attribute_values = models.ManyToManyField(
        ProductAttributeValue,
        related_name="product_inventories",
        blank=True,
    )
    stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
    )
    is_active = models.BooleanField(
        verbose_name=_("Product Visibility"),
        help_text=_("True = Product Visible"),
        default=True,
        unique=False,
        null=False,
        blank=False,
    )
    retail_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Recommended Retail Price"),
        help_text=_("Maximum price 99999999.99"),
        validators=[MinValueValidator(0)],
        unique=False,
        null=False,
        blank=False,
    )
    store_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Regular Store Price"),
        help_text=_("Maximum price 99999999.99"),
        validators=[MinValueValidator(0)],
        unique=False,
        null=False,
        blank=False,
    )
    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Sale Price"),
        help_text=_("Maximum price 99999999.99"),
        validators=[MinValueValidator(0)],
        unique=False,
        null=True,
        blank=True,
    )
    weight = models.FloatField(
        verbose_name=_("Product Weight"),
        unique=False,
        null=False,
        blank=False,
        validators=[MinValueValidator(0)],
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Date Sub-Product Created"),
        help_text=_("Format: Y-m-d H:M:S"),
        editable=False,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Date Sub-Product Updated"),
        help_text=_("Format: Y-m-d H:M:S"),
    )

    class Meta:
        unique_together = ("sku", "upc")

    def __str__(self):
        return f"{self.product.name} - {self.sku}"
