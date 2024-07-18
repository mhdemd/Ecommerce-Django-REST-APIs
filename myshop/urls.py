from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = i18n_patterns(
    path("admin/", admin.site.urls),
    path("shop/", include("shop.urls", namespace="shop")),
    path("zarinpal/", include("zarinpal.urls", namespace="zarinpal")),
    path("checkout/", include("checkout.urls", namespace="checkout")),
    path("cart/", include("cart.urls", namespace="cart")),
    path("orders/", include("orders.urls", namespace="orders")),
    path("account/", include("account.urls", namespace="account")),
    path("rosetta/", include("rosetta.urls")),
    path("", include("portfolio.urls", namespace="portfolio")),
    path("__debug__/", include("debug_toolbar.urls")),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
