from mptt.admin import DraggableMPTTAdmin

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from .models import (
    Brand,
    Category,
    Media,
    Product,
    ProductAttribute,
    ProductAttributeValue,
    ProductInventory,
    ProductReview,
    ProductType,
)


class MediaAdminForm(ModelForm):
    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image:
            # Check the image size
            if image.size > 200 * 1024:  # Converted 200 kilobytes to bytes
                raise forms.ValidationError(
                    "Image size should be less than 200 kilobytes."
                )
        return image

    class Meta:
        model = Media
        fields = "__all__"


class MediaInline(admin.TabularInline):
    model = Media
    form = MediaAdminForm


class ProductInventoryInline(admin.TabularInline):
    model = ProductInventory
    extra = 1
    exclude = ("sku", "upc", "product_type")


class CategoryAdmin(DraggableMPTTAdmin):
    list_display = (
        "tree_actions",
        "indented_title",
        "is_active",
    )
    list_display_links = ("indented_title",)
    list_filter = ("is_active",)
    search_fields = (
        "name",
        "slug",
    )
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Category, CategoryAdmin)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [MediaInline, ProductInventoryInline]
    list_filter = (
        "category",
        "is_active",
        "brand",
    )
    search_fields = ["name", "category__name"]
    exclude = ["users_wishlist", "web_id"]


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):
    list_display = ("product_attribute", "attribute_value")


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "product",
        "review",
        "rating",
    )
