from django.contrib import admin

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
    Wishlist,
)

admin.site.register(Product)
admin.site.register(Media)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(ProductInventory)
admin.site.register(ProductAttribute)
admin.site.register(ProductAttributeValue)
admin.site.register(ProductType)
admin.site.register(ProductReview)
admin.site.register(Wishlist)
