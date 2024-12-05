from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Media(models.Model):
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="media",
        verbose_name=_("Product"),
    )
    image = models.ImageField(
        upload_to="images/",
        default="images/default.png",
        verbose_name=_("Product Image"),
        help_text=_("Required, default: 'default.png'"),
    )
    is_feature = models.BooleanField(
        default=False,
        verbose_name=_("Product Default Image"),
        help_text=_("Default: False, True = Default Image"),
    )
    ordering = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Image Ordering"),
        help_text=_("Define the order of images"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Date Image Created"),
        help_text=_("Format: Y-m-d H:M:S"),
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
        unique=True,
        verbose_name=_("Product Website ID"),
        help_text=_("Required, unique"),
    )
    slug = models.SlugField(
        max_length=255,
        verbose_name=_("Product Safe URL"),
        help_text=_("Required, letters, numbers, underscores, or hyphens"),
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("Product Name"),
        help_text=_("Required, max 255 characters"),
    )
    description = models.TextField(
        verbose_name=_("Product Description"),
        help_text=_("Required"),
    )
    brand = models.ForeignKey(
        "Brand",
        related_name="products",
        on_delete=models.PROTECT,
        verbose_name=_("Brand"),
    )
    category = models.ForeignKey(
        "Category",
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name=_("Product Category"),
        help_text=_("Required"),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Product Visibility"),
        help_text=_("True = Product Visible"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Date Product Created"),
        help_text=_("Format: Y-m-d H:M:S"),
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
        verbose_name=_("Users Wishlist"),
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
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def get_absolute_url(self):
        return reverse("shop:product_detail", args=[self.id, self.slug])

    def __str__(self):
        return self.name

    def total_stock(self):
        return (
            self.product_inventory.aggregate(total_stock=models.Sum("stock"))[
                "total_stock"
            ]
            or 0
        )
