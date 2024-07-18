from django.core.cache import cache
from shop.models import Category

from .cart import Cart


def cart(request):
    return {"cart": Cart(request)}


def categories(request):
    # توجه: شما می‌توانید زمان انقضا را تنظیم کنید (مثلاً 3600 برای یک ساعت)
    cache_key = "categories_with_products"
    cached_categories = cache.get(cache_key)

    if cached_categories is not None:
        # اگر نتایج در کش موجود باشند، آنها را برگردانید
        return {"categories": cached_categories}

    # اگر نتایج در کش نباشند، آنها را محاسبه کنید و در کش قرار دهید
    categories_with_products = Category.objects.filter(level=1).prefetch_related(
        "children__children"
    )

    cache.set(cache_key, categories_with_products, 36)  # 3600 ثانیه معادل یک ساعت است

    return {"categories": categories_with_products}


def wishlist_count(request):
    if request.user.is_authenticated:
        user_wishlist_ids = list(
            request.user.user_wishlist.all().values_list("id", flat=True)
        )
        wishlist_count = len(user_wishlist_ids)
        return {
            "wishlist_count": wishlist_count,
            "user_wishlist_ids": user_wishlist_ids,
        }
    else:
        return {
            "wishlist_count": 0,
            "user_wishlist_ids": [],
        }
