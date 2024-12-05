from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey


class Media(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="media_product"
    )
    image = models.ImageField(
        verbose_name=_("Product Image"),
        help_text=_("Required, default: 'default.png'"),
        upload_to="images/",
        default="images/default.png",
        unique=False,
        null=False,
        blank=False,
    )
    is_feature = models.BooleanField(
        verbose_name=_("Product Default Image"),
        help_text=_("Default: False, True = Default Image"),
        default=False,
    )
    ordering = models.PositiveIntegerField(
        verbose_name=_("Image Ordering"),
        help_text=_("Define the order of images"),
        default=0,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Date Image Created"),
        help_text=_("Format: Y-m-d H:M:S"),
        editable=False,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Date Image Updated"),
        help_text=_("Format: Y-m-d H:M:S"),
    )

    class Meta:
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")
        ordering = ["ordering"]

    def __str__(self):
        return f"Image for {self.product.name}"


class Product(models.Model):
    web_id = models.CharField(
        max_length=50,
        verbose_name=_("Product Website ID"),
        help_text=_("Required, unique"),
        unique=True,
        null=False,
        blank=False,
    )
    slug = models.SlugField(
        max_length=255,
        verbose_name=_("Product Safe URL"),
        help_text=_("Required, letters, numbers, underscores, or hyphens"),
        unique=False,
        null=False,
        blank=False,
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("Product Name"),
        help_text=_("Required, max 255 characters"),
        unique=False,
        null=False,
        blank=False,
    )
    description = models.TextField(
        verbose_name=_("Product Description"),
        help_text=_("Required"),
        unique=False,
        null=False,
        blank=False,
    )
    brand = models.ForeignKey(
        Brand,
        related_name="products",
        on_delete=models.PROTECT,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name=_("Product Category"),
        help_text=_("Required"),
        unique=False,
        null=False,
        blank=False,
    )
    is_active = models.BooleanField(
        verbose_name=_("Product Visibility"),
        help_text=_("True = Product Visible"),
        default=True,
        unique=False,
        null=False,
        blank=False,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Date Product Created"),
        help_text=_("Format: Y-m-d H:M:S"),
        editable=False,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Date Product Last Updated"),
        help_text=_("Format: Y-m-d H:M:S"),
    )
    users_wishlist = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="Wishlist",
        related_name="wishlisted_products",
        blank=True,
    )

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["id", "slug"]),
            models.Index(fields=["name"]),
            models.Index(fields=["-created_at"]),
            models.Index(fields=["brand"]),
            models.Index(fields=["category"]),
        ]
        unique_together = ("web_id", "slug")

    def get_absolute_url(self):
        return reverse("shop:product_detail", args=[int(self.id), self.slug])

    def __str__(self):
        return self.name

    def total_stock(self):
        return (
            self.product_inventory.aggregate(total_stock=models.Sum("stock"))[
                "total_stock"
            ]
            or 0
        )
