from django.db.models import OuterRef, Subquery
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from shop.models import Product, ProductInventory

from .cart import Cart
from .forms import CartAddProductForm


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(
        Product.objects.annotate(
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
        ).prefetch_related("product_inventory", "media_product"),
        id=product_id,
    )

    sale_price = {}
    variety_choices = []
    variety_name = None

    for inventory in product.product_inventory.select_related("attribute_values").all():
        variety_id = inventory.id
        variety_value = inventory.attribute_values.attribute_value
        if not variety_name:
            variety_name = inventory.attribute_values.product_attribute

        price = inventory.sale_price
        sale_price[variety_id] = price
        variety_choices.append((variety_id, variety_value))

    cart_quantities_dict = cart.get_quantity_for_product()

    # Create a form instance and populate it with data from the request:
    form = CartAddProductForm(
        product=product,
        cart_quantities_dict=cart_quantities_dict,
        sale_price=sale_price,
        variety_choices=variety_choices,
        variety_name=variety_name,
        data=request.POST,
    )

    if form.is_valid():
        form_cleaned = form.cleaned_data
        # This is first arg in 'variety_choices' in form.py
        product_inventory_id = form_cleaned.get("variety")
        product_inventory = get_object_or_404(ProductInventory, id=product_inventory_id)

        quantity = form_cleaned["quantity"]
        override_quantity = form_cleaned["override"]

        # variety extraction from product inventory database
        variety = product_inventory.attribute_values.attribute_value

        # Price extraction from product inventory database
        sale_price = float(product_inventory.sale_price)

        cart.add(
            product_id=product_id,
            product_inventory_id=product_inventory_id,
            variety=variety,
            sale_price=sale_price,
            quantity=quantity,
            override_quantity=override_quantity,
        )
        return redirect("cart:cart_detail")
    else:
        # Form is not valid, stay on the product details page
        return render(
            request,
            "shop/product/product_detail.html",
            {"product": product, "cart_product_form": form},
        )


@require_POST
def cart_remove(request, product_inventory_id):
    cart = Cart(request)
    product_inventory = get_object_or_404(ProductInventory, id=product_inventory_id)
    cart.remove(product_inventory)
    return redirect("cart:cart_detail")


def cart_detail(request):
    cart = Cart(request)

    remaining_time = cart.get_expiry_time_remaining()

    if remaining_time is not None:
        remaining_minutes, remaining_seconds = remaining_time
    else:
        remaining_minutes, remaining_seconds = 0, 0

    print(remaining_minutes, ":", remaining_seconds)

    context = {
        "remaining_minutes": int(remaining_minutes),
        "remaining_seconds": int(remaining_seconds),
    }
    for item in cart:
        product_id = item["product_id"]

        product = get_object_or_404(
            Product.objects.annotate(
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
            ).prefetch_related("product_inventory", "media_product"),
            id=product_id,
        )

        sale_price = {}
        variety_choices = []
        variety_name = None

        for inventory in product.product_inventory.select_related(
            "attribute_values"
        ).all():
            variety_id = inventory.id
            variety_value = inventory.attribute_values.attribute_value
            if not variety_name:
                variety_name = inventory.attribute_values.product_attribute

            price = inventory.sale_price
            sale_price[variety_id] = price
            variety_choices.append((variety_id, variety_value))

        # In order to be able to override the quantity on the cart details page
        item["update_quantity_form"] = CartAddProductForm(
            product,
            sale_price=sale_price,
            variety_choices=variety_choices,
            variety_name=variety_name,
            initial={
                "quantity": item["quantity"],
                "override": True,
            },
        )

    return render(
        request, "cart/detail.html", {"cart": cart, "remaining_time": context}
    )
