from django.urls import path

from . import views

app_name = "shop"

urlpatterns = [
    path("", views.home, name="home"),
    path("help/", views.help, name="help"),
    path("search/", views.search_view, name="search"),
    path("add_review/<int:id>/<slug:slug>/", views.add_review, name="add_review"),
    path(
        "filtering_view/<slug:category_slug>/",
        views.filtering_view,
        name="filtering_view",
    ),
    path("sorting_view/<slug:category_slug>/", views.sorting_view, name="sorting_view"),
    path("<slug:category_slug>/", views.product_list, name="product_list_by_category"),
    path("<int:id>/<slug:slug>/", views.product_detail, name="product_detail"),
    path(
        "show_categories/<slug:category_slug>/",
        views.show_categories,
        name="show_categories",
    ),
    # API
    path("api/categories/", views.get_categories_as_json, name="categories-json"),
    path("api/products/", views.get_products_as_json, name="products-json"),
    path(
        "api/product_inventory/",
        views.get_product_inventory_as_json,
        name="product_inventory-json",
    ),
    path(
        "api/product_attribute_values/",
        views.get_product_attribute_values_as_json,
        name="product_attribute_values-json",
    ),
    path(
        "api/brands/",
        views.get_brands_as_json,
        name="brands-json",
    ),
    path(
        "api/media/",
        views.get_media_as_json,
        name="media-json",
    ),
    path(
        "api/delivery_options/",
        views.get_delivery_options_as_json,
        name="delivery_options-json",
    ),
]
