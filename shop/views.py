from cart.forms import CartAddProductForm
from checkout.models import DeliveryOptions
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Avg, Min, OuterRef, Prefetch, Q, Subquery
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import ProductAttributeForm, ProductReviewForm, SortingForm
from .models import Media  # For API
from .models import Product  # For API
from .models import ProductAttributeValue  # For API
from .models import Brand, Category, ProductInventory, ProductReview  # For API


# Help
def help(request):
    return render(
        request,
        "shop/product/help.html",
    )


# Show categories
def show_categories(request, category_slug):
    category = get_object_or_404(
        Category.objects.prefetch_related("children"), slug=category_slug
    )
    # 1. بررسی زیرمجموعه داشتن دسته‌بندی
    subcategories = category.children.all()
    if subcategories.exists():
        print("Subcategories exist")
        return render(
            request,
            "shop/product/show_categories.html",
            {"subcategories": subcategories},
        )

    print("No subcategories")

    # اگر زیرمجموعه‌ای وجود نداشت
    return product_list(request, category_slug=category_slug)


# Home
def home(request):
    # Cheapest Products
    first_sale_price = ProductInventory.objects.filter(
        product=OuterRef("pk"), is_active=True
    ).values("sale_price")[:1]

    first_retail_price = ProductInventory.objects.filter(
        product=OuterRef("pk"), is_active=True
    ).values("retail_price")[:1]

    cheapest_products = (
        Product.objects.filter(is_active=True, product_inventory__is_active=True)
        .annotate(
            min_sale_price=Min("product_inventory__sale_price"),
            first_sale_price=Subquery(first_sale_price),
            first_retail_price=Subquery(first_retail_price),
            average_rating=Avg("reviews__rating"),
        )
        .order_by("-min_sale_price")[:8]
        .prefetch_related(
            Prefetch(
                "media_product",
                queryset=Media.objects.filter(Q(is_feature=True) | Q(is_feature=False)),
                to_attr="featured_images",
            ),
            Prefetch(
                "product_inventory",
                queryset=ProductInventory.objects.defer(
                    "sku",
                    "upc",
                    "product_type_id",
                    "attribute_values_id",
                    "stock",
                    "weight",
                    "created_at",
                    "updated_at",
                ).filter(is_active=True),
                to_attr="filtered_inventories",
            ),
            "reviews",
        )
        .defer(
            "description",
            "updated_at",
            "created_at",
            "category_id",
            "brand_id",
            "web_id",
        )
    )

    # Latest Products
    latest_products = (
        Product.objects.order_by("-created_at")[49:57]
        .prefetch_related(
            Prefetch(
                "media_product",
                queryset=Media.objects.filter(Q(is_feature=True) | Q(is_feature=False)),
                to_attr="featured_images",
            ),
            Prefetch(
                "product_inventory",
                queryset=ProductInventory.objects.defer(
                    "sku",
                    "upc",
                    "product_type_id",
                    "attribute_values_id",
                    "stock",
                    "weight",
                    "created_at",
                    "updated_at",
                ).filter(is_active=True),
                to_attr="filtered_inventories",
            ),
            "reviews",
        )
        .annotate(
            first_sale_price=Subquery(
                ProductInventory.objects.filter(product=OuterRef("pk")).values(
                    "sale_price"
                )[:1]
            ),
            first_retail_price=Subquery(
                ProductInventory.objects.filter(product=OuterRef("pk")).values(
                    "retail_price"
                )[:1]
            ),
            average_rating=Avg("reviews__rating"),
        )
        .defer(
            "description",
            "updated_at",
            "created_at",
            "category_id",
            "brand_id",
            "web_id",
        )
    )

    # 8 categories
    categories_8 = Category.objects.filter(level=2)[:8]

    context = {
        "cheapest_products": cheapest_products,
        "latest_products": latest_products,
        "categories_8": categories_8,
    }

    return render(request, "shop/product/home.html", context)


# Product list
def get_products_for_category(
    category_slug,
    size_vals=None,
    color_vals=None,
    price_vals=None,
    sort_val=None,
):
    cache_key = f"products_for_category_{category_slug}"
    cached_data = cache.get(cache_key)

    # کش نداشته باشیم یا فیلتر و ترتیب داشته باشیم
    if (
        not cached_data
        or size_vals is not None
        or color_vals is not None
        or price_vals is not None
        or sort_val is not None
    ):
        category = get_object_or_404(Category.objects.only("name"), slug=category_slug)

        # Dynamic Filter
        # Create condition for size filter
        if size_vals:
            size_condition = Q(
                product_inventory__attribute_values__attribute_value__in=size_vals
            )
        else:
            size_condition = Q()

        # Create condition for color filter
        if color_vals:
            color_condition = Q(
                product_inventory__attribute_values__attribute_value__in=color_vals
            )
        else:
            color_condition = Q()

        # Create condition for price filter
        if price_vals:
            if price_vals == "over $100":
                min_price = 100
                max_price = 10000000

            elif price_vals == "all":
                min_price = 0
                max_price = 10000000
            else:
                price_values = price_vals.split(" - ")
                min_price = int(price_values[0].replace("$", ""))
                max_price = int(price_values[1].replace("$", ""))

            price_condition = Q(product_inventory__sale_price__gte=min_price) & Q(
                product_inventory__sale_price__lte=max_price
            )
        else:
            price_condition = Q()

        # Query
        products = (
            Product.objects.filter(category=category)
            .only("id", "name", "slug")
            .annotate(
                first_sale_price=Subquery(
                    ProductInventory.objects.filter(product=OuterRef("pk")).values(
                        "sale_price"
                    )[:1]
                ),
                first_retail_price=Subquery(
                    ProductInventory.objects.filter(product=OuterRef("pk")).values(
                        "retail_price"
                    )[:1]
                ),
                average_rating=Avg("reviews__rating"),
            )
            .prefetch_related(
                Prefetch(
                    "media_product",
                    queryset=Media.objects.filter(
                        Q(is_feature=True) | Q(is_feature=False)
                    ),
                    to_attr="featured_images",
                ),
                "reviews",
            )
            .filter(size_condition, price_condition, color_condition)
        )

        # Apply sorting based on the sort_val option
        if sort_val == "Latest":
            products = products.order_by("-created_at")

        elif sort_val == "Best Rating":
            products = products.order_by("-reviews__rating")

        elif sort_val == "Most Expensive":
            products = products.order_by("-product_inventory__sale_price")

        elif sort_val == "Least Expensive":
            products = products.order_by("product_inventory__sale_price")

        # Save in cache if we don't have filter and sort
        if (
            size_vals is None
            and color_vals is None
            and price_vals is None
            and sort_val is None
        ):
            cached_data = (category, products)
            cache.set(cache_key, cached_data, 500)

    else:
        print("use cach")
        category, products = cached_data

    return category, products


def filtering_view(request, category_slug):
    print("filtering_view")
    if request.method == "POST":
        selected_size = request.session.get("selected_size", None)
        selected_color = request.session.get("selected_color", None)
        selected_price = request.session.get("selected_price", None)

        product_attribute_form = ProductAttributeForm(request.POST)
        if product_attribute_form.is_valid():
            print("product_attribute_form.is_valid()")

            size_vals = []
            color_vals = []

            if "size" in product_attribute_form.cleaned_data:
                size = product_attribute_form.cleaned_data["size"]
                size_vals += size
                selected_size = size

            if "color" in product_attribute_form.cleaned_data:
                color = product_attribute_form.cleaned_data["color"]
                color_vals += color
                selected_color = color

            price_vals = product_attribute_form.cleaned_data["price"]
            selected_price = price_vals

            request.session["filters_size_vals"] = size_vals
            request.session["filters_color_vals"] = color_vals
            request.session["filters_price_vals"] = price_vals
            request.session["selected_size"] = selected_size
            request.session["selected_color"] = selected_color
            request.session["selected_price"] = selected_price

        return product_list(
            request,
            category_slug,
            selected_size=selected_size,
            selected_color=selected_color,
            selected_price=selected_price,
            size_vals=size_vals,
            color_vals=color_vals,
            product_attribute_form=product_attribute_form,
        )

    else:
        return product_list(request, category_slug)


def sorting_view(request, category_slug):
    print("sorting_view")
    if request.method == "POST":
        selected_sort = request.session.get("selected_sort", None)

        sorting_form = SortingForm(request.POST)

        if sorting_form.is_valid():
            print("sorting_form.is_valid()")
            selected_sort = sorting_form.cleaned_data["sort"]

            request.session["selected_sort"] = selected_sort

        return product_list(
            request,
            category_slug,
            selected_sort=selected_sort,
            sorting_form=sorting_form,
        )

    else:
        return product_list(request, category_slug)


def product_list(
    request,
    category_slug,
    # filter
    category=None,
    selected_size=None,
    selected_color=None,
    selected_price=None,
    size_vals=None,
    color_vals=None,
    product_attribute_form=None,
    # sort
    selected_sort=None,
    sorting_form=None,
):
    print(
        "selected_size is:",
        selected_size,
        "selected_color is:",
        selected_color,
        "selected_price is:",
        selected_price,
        "selected_sort is:",
        selected_sort,
    )
    products_per_page = 15
    page = request.GET.get("page")

    if selected_size or selected_color or selected_price:
        selected_sort = request.session.get("selected_sort", None)

        category, products = get_products_for_category(
            category_slug,
            size_vals=size_vals,
            color_vals=color_vals,
            price_vals=selected_price,
            sort_val=selected_sort,
        )

        sorting_form = SortingForm(
            initial={
                "sort": selected_sort if selected_sort is not None else "Sorting",
            },
        )

    elif selected_sort:
        size_vals = request.session.get("filters_size_vals", [])
        color_vals = request.session.get("filters_color_vals", [])
        price_vals = request.session.get("filters_price_vals", None)
        selected_size = request.session.get("selected_size", None)
        selected_color = request.session.get("selected_color", None)
        selected_price = request.session.get("selected_price", None)

        category, products = get_products_for_category(
            category_slug,
            size_vals=size_vals,
            color_vals=color_vals,
            price_vals=selected_price,
            sort_val=selected_sort,
        )

        product_attribute_form = ProductAttributeForm(
            initial={
                "size": selected_size,
                "color": selected_color,
                "price": selected_price,
            },
        )

    else:
        # Delete size, color, price, ... session if "?page" not in url
        if request.GET.get("page") is None:
            print("delete session")
            if "selected_sort" in request.session:
                del request.session["selected_sort"]
            if "selected_size" in request.session:
                del request.session["selected_size"]
            if "selected_color" in request.session:
                del request.session["selected_color"]
            if "selected_price" in request.session:
                del request.session["selected_price"]
            if "filters_size_vals" in request.session:
                del request.session["filters_size_vals"]
            if "filters_color_vals" in request.session:
                del request.session["filters_color_vals"]
            if "filters_price_vals" in request.session:
                del request.session["filters_price_vals"]

            size_vals = None
            color_vals = None
            price_vals = None
            selected_size = None
            selected_color = None
            selected_price = None
            selected_sort = "Sorting"

        # When the request comes from below, the sessions shouldn't be cleared.
        # 1.Changing page

        else:
            print("load data from session")
            size_vals = request.session.get("filters_size_vals", [])
            color_vals = request.session.get("filters_color_vals", [])
            price_vals = request.session.get("filters_price_vals", None)
            selected_size = request.session.get("selected_size", None)
            selected_color = request.session.get("selected_color", None)
            selected_price = request.session.get("selected_price", None)
            selected_sort = request.session.get("selected_sort", None)

        category, products = get_products_for_category(
            category_slug,
            size_vals=size_vals,
            color_vals=color_vals,
            price_vals=price_vals,
            sort_val=selected_sort,
        )

        product_attribute_form = ProductAttributeForm(
            initial={
                "size": selected_size,
                "color": selected_color,
                "price": selected_price,
            },
        )

        sorting_form = SortingForm(
            initial={
                "sort": selected_sort,
            },
        )

    paginator = Paginator(products, products_per_page)
    page_obj = paginator.get_page(page)

    return render(
        request,
        "shop/product/category_list.html",
        {
            "category": category,
            "products": page_obj,
            "product_attribute_form": product_attribute_form,
            "sorting_form": sorting_form,
        },
    )


# Product detail
def product_detail(request, id, slug):
    # product
    product = get_object_or_404(
        Product.objects.filter(id=id, slug=slug, is_active=True)
        .annotate(
            first_sale_price=Subquery(
                ProductInventory.objects.filter(product=OuterRef("pk")).values(
                    "sale_price"
                )[:1]
            ),
            first_retail_price=Subquery(
                ProductInventory.objects.filter(product=OuterRef("pk")).values(
                    "retail_price"
                )[:1]
            ),
            average_rating=Avg("reviews__rating"),
        )
        .prefetch_related(
            Prefetch(
                "media_product",
                queryset=Media.objects.filter(Q(is_feature=True) | Q(is_feature=False)),
                to_attr="featured_images",
            ),
            "product_inventory",
            "media_product",
            "reviews",
        )
    )

    # product_images
    product_images = product.media_product.all()

    # cart_product_form
    sale_price = {}
    variety_choices = []
    variety_name = None

    for inventory in product.product_inventory.all():
        variety_id = inventory.id
        variety_value = inventory.attribute_values.attribute_value
        if not variety_name:
            variety_name = inventory.attribute_values.product_attribute

        price = inventory.sale_price
        sale_price[variety_id] = price
        variety_choices.append((variety_id, variety_value))

    cart_product_form = CartAddProductForm(
        product=product,
        sale_price=sale_price,
        variety_choices=variety_choices,
        variety_name=variety_name,
    )

    # review_form
    review_form = ProductReviewForm()

    # user_has_reviewed
    try:
        user_has_reviewed = ProductReview.objects.filter(
            product=product, user=request.user
        ).exists()
    except:
        user_has_reviewed = None

    # product_reviews = ProductReview.objects.filter(product=product)
    # average_rating = product_reviews.aggregate(Avg("rating"))["rating__avg"]

    # similar_products
    current_category = product.category

    similar_products = (
        Product.objects.filter(Q(category=current_category))
        .exclude(id=product.id)
        .annotate(
            first_sale_price=Subquery(
                ProductInventory.objects.filter(product=OuterRef("pk")).values(
                    "sale_price"
                )[:1]
            ),
            first_retail_price=Subquery(
                ProductInventory.objects.filter(product=OuterRef("pk")).values(
                    "retail_price"
                )[:1]
            ),
            average_rating=Avg("reviews__rating"),
        )
        .prefetch_related(
            Prefetch(
                "media_product",
                queryset=Media.objects.filter(Q(is_feature=True) | Q(is_feature=False)),
                to_attr="featured_images",
            ),
            "media_product",
        )[:5]
    )

    return render(
        request,
        "shop/product/product_detail.html",
        {
            "product": product,
            "product_images": product_images,
            "cart_product_form": cart_product_form,
            "review_form": review_form,
            "user_has_reviewed": user_has_reviewed,
            "similar_products": similar_products,
        },
    )


@login_required
def add_review(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug)

    if request.method == "POST":
        review_form = ProductReviewForm(request.POST)

        if review_form.is_valid():
            new_review = review_form.save(commit=False)
            new_review.product = product
            new_review.user = request.user
            new_review.rating = request.POST.get("rating")
            new_review.save()
            return redirect(
                reverse("shop:product_detail", kwargs={"id": id, "slug": slug})
            )

        else:
            errors = dict(review_form.errors.items())
            return JsonResponse({"errors": errors}, status=400)

    return redirect(reverse("shop:product_detail", kwargs={"id": id, "slug": slug}))


# Search
def search_view(request):
    query = request.GET.get("q")

    products = (
        Product.objects.filter(name__icontains=query)
        .order_by("-created_at")
        .only("id", "name", "slug")
        .annotate(
            first_sale_price=Subquery(
                ProductInventory.objects.filter(product=OuterRef("pk")).values(
                    "sale_price"
                )[:1]
            ),
            first_retail_price=Subquery(
                ProductInventory.objects.filter(product=OuterRef("pk")).values(
                    "retail_price"
                )[:1]
            ),
            average_rating=Avg("reviews__rating"),
        )
        .prefetch_related("media_product")
    )[:30]

    context = {
        "products": products,
        "query": query,
    }
    return render(request, "shop/search.html", context)


# ***API***
from django.core import serializers


def get_categories_as_json(request):
    categories = Category.objects.all()
    data = serializers.serialize(
        "json",
        categories,
        fields=(
            "name",
            "slug",
            "parent",
            "is_active",
            "lft",
            "rght",
            "tree_id",
            "level",
        ),
    )
    response = HttpResponse(data, content_type="application/json")
    response["Content-Disposition"] = 'attachment; filename="db_category_fixture.json"'
    return response


def get_products_as_json(request):
    products = Product.objects.all()
    data = serializers.serialize(
        "json",
        products,
        fields=(
            "web_id",
            "slug",
            "name",
            "description",
            "brand",
            "category",
            "is_active",
            "created_at",
            "updated_at",
            "users_wishlist",
        ),
    )
    response = HttpResponse(data, content_type="application/json")
    response["Content-Disposition"] = 'attachment; filename="db_product_fixture.json"'
    return response


def get_product_inventory_as_json(request):
    product_inventory = ProductInventory.objects.all()
    data = serializers.serialize(
        "json",
        product_inventory,
        fields=(
            "sku",
            "upc",
            "product_type",
            "product",
            "attribute_values",
            "stock",
            "is_active",
            "retail_price",
            "store_price",
            "sale_price",
            "weight",
            "created_at",
            "updated_at",
        ),
    )
    response = HttpResponse(data, content_type="application/json")
    response[
        "Content-Disposition"
    ] = 'attachment; filename="db_product_inventory_fixture.json"'
    return response


def get_product_attribute_values_as_json(request):
    attribute_values = ProductAttributeValue.objects.all()
    data = serializers.serialize(
        "json",
        attribute_values,
        fields=(
            "product_attribute",
            "attribute_value",
        ),
    )
    response = HttpResponse(data, content_type="application/json")
    response[
        "Content-Disposition"
    ] = 'attachment; filename="db_product_attribute_value_fixture.json"'
    return response


def get_brands_as_json(request):
    brands = Brand.objects.all()
    data = serializers.serialize(
        "json",
        brands,
        fields=("name",),
    )
    response = HttpResponse(data, content_type="application/json")
    response["Content-Disposition"] = 'attachment; filename="db_brand_fixture.json"'
    return response


def get_media_as_json(request):
    media = Media.objects.select_related("product").all()
    data = serializers.serialize(
        "json",
        media,
        fields=("image", "is_feature", "created_at", "updated_at", "product"),
    )

    response = HttpResponse(data, content_type="application/json")
    response["Content-Disposition"] = 'attachment; filename="db_media_fixture.json"'
    return response


def get_delivery_options_as_json(request):
    delivery_options = DeliveryOptions.objects.all()
    data = serializers.serialize(
        "json",
        delivery_options,
        fields=(
            "delivery_name",
            "delivery_price",
            "delivery_method",
            "delivery_timeframe",
            "delivery_window",
            "order",
            "is_active",
        ),
    )

    response = HttpResponse(data, content_type="application/json")
    response[
        "Content-Disposition"
    ] = 'attachment; filename="db_delivery_options_fixture.json"'
    return response
