from django.contrib import admin

from .models import (  # Brand,; Category,; ProductReview,; Wishlist,
    Media,
    Product,
    ProductAttribute,
    ProductAttributeValue,
    ProductInventory,
    ProductType,
)

admin.site.register(Product)
admin.site.register(Media)
# admin.site.register(Category)
# admin.site.register(Brand)
admin.site.register(ProductInventory)
admin.site.register(ProductAttribute)
admin.site.register(ProductAttributeValue)
admin.site.register(ProductType)
# admin.site.register(ProductReview)
# admin.site.register(Wishlist)
