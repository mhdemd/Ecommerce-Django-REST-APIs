from mptt.models import MPTTModel, TreeForeignKey

from account.models import UserBase
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Brand(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name=_("Brand Name"),
        help_text=_("Required, unique, max 255 characters"),
        unique=True,
        null=False,
        blank=False,
    )

    def __str__(self):
        return self.name


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


class Product(models.Model):
    web_id = models.CharField(
        max_length=50,
        verbose_name=_("Product Website ID"),
        help_text=_("Required, unique"),
        unique=False,
        null=True,
        blank=True,
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
    brand = models.ForeignKey(Brand, related_name="brand", on_delete=models.PROTECT)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="product",
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
        related_name="user_wishlist",
        blank=True,
    )

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["id", "slug"]),
            models.Index(fields=["name"]),
            models.Index(fields=["-created_at"]),
        ]

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


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")


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
        ProductAttribute, related_name="product_attribute", on_delete=models.CASCADE
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


class ProductInventory(models.Model):
    sku = models.CharField(
        max_length=20,
        verbose_name=_("Stock Keeping Unit (SKU)"),
        help_text=_("Required, unique, max 20 characters"),
        unique=False,
        null=True,
        blank=True,
    )
    upc = models.CharField(
        max_length=12,
        verbose_name=_("Universal Product Code (UPC)"),
        help_text=_("Required, unique, max 12 characters"),
        unique=False,
        null=True,
        blank=True,
    )
    product_type = models.ForeignKey(
        ProductType,
        related_name="product_type",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    product = models.ForeignKey(
        Product, related_name="product_inventory", on_delete=models.CASCADE
    )
    attribute_values = models.ForeignKey(
        ProductAttributeValue,
        related_name="product_inventories",
        on_delete=models.PROTECT,
    )
    stock = models.IntegerField(default=0)
    is_active = models.BooleanField(
        verbose_name=_("Product Visibility"),
        help_text=_("True = Product Visible"),
        default=True,
        unique=False,
        null=False,
        blank=False,
    )
    retail_price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_("Recommended Retail Price"),
        help_text=_("Maximum price 999.99"),
        error_messages={
            "name": {"max_length": _("The price must be between 0 and 999.99.")},
        },
        unique=False,
        null=False,
        blank=False,
    )
    store_price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_("Regular Store Price"),
        help_text=_("Maximum price 999.99"),
        error_messages={
            "name": {"max_length": _("The price must be between 0 and 999.99.")},
        },
        unique=False,
        null=False,
        blank=False,
    )
    sale_price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_("Sale Price"),
        help_text=_("Maximum price 999.99"),
        error_messages={
            "name": {"max_length": _("The price must be between 0 and 999.99.")},
        },
        unique=False,
        null=False,
        blank=False,
    )
    weight = models.FloatField(
        verbose_name=_("Product Weight"), unique=False, null=False, blank=False
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

    def __str__(self):
        return self.product.name


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
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Product Visibility"),
        help_text=_("Format: Y-m-d H:M:S"),
        editable=False,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Date Sub-Product Created"),
        help_text=_("Format: Y-m-d H:M:S"),
    )

    class Meta:
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")


class ProductReview(models.Model):
    user = models.ForeignKey(UserBase, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    review = models.TextField()
    rating = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)], default=None
    )
    date = models.DateTimeField(auto_now_add=True)
    show_name = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = _("Product Reviews")
        ordering = ["-date"]

    def __str__(self):
        return self.product.name

    def get_rating(self):
        return self.rating
