from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .attribute import ProductAttributeValue, ProductType
from .product import Product


class ProductInventory(models.Model):
    sku = models.CharField(
        max_length=20,
        verbose_name=_("Stock Keeping Unit (SKU)"),
        help_text=_("Required, unique, max 20 characters"),
        unique=True,
    )
    upc = models.CharField(
        max_length=12,
        verbose_name=_("Universal Product Code (UPC)"),
        help_text=_("Required, unique, max 12 characters"),
        unique=True,
    )
    product_type = models.ForeignKey(
        ProductType,
        related_name="product_inventories",
        on_delete=models.PROTECT,
    )
    product = models.ForeignKey(
        Product,
        related_name="product_inventory",
        on_delete=models.CASCADE,
    )
    attribute_values = models.ManyToManyField(
        ProductAttributeValue,
        related_name="product_inventories",
        blank=True,
    )
    stock = models.IntegerField(validators=[MinValueValidator(0)])
    is_active = models.BooleanField(
        verbose_name=_("Product Visibility"),
        help_text=_("True = Product Visible"),
        default=True,
    )
    retail_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0"))]
    )

    store_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0"))]
    )

    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        null=True,
        blank=True,
    )

    weight = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0"))]
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Date Sub-Product Created"),
        help_text=_("Format: Y-m-d H:M:S"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Date Sub-Product Updated"),
        help_text=_("Format: Y-m-d H:M:S"),
    )

    class Meta:
        indexes = [
            models.Index(fields=["sku"]),
            models.Index(fields=["upc"]),
            models.Index(fields=["product"]),
        ]
        verbose_name = _("Product Inventory")
        verbose_name_plural = _("Product Inventories")

    def __str__(self):
        return f"{self.product.name} - {self.sku}"

    def get_absolute_url(self):
        return reverse("product_inventory_detail", args=[self.sku])
