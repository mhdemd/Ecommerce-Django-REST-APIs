import weasyprint

from account.models import Address
from cart.cart import Cart
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse

from .models import Order, OrderItem
from .tasks import order_created


@login_required
def order_address(request):
    cart = Cart(request)
    user = request.user
    address = (
        Address.objects.filter(Q(user=user, default=True) | Q(user=user, default=False))
        .order_by("-default", "-created_at")
        .first()
    )
    return render(
        request,
        "orders/order/create.html",
        {"cart": cart, "address": address},
    )


@login_required
def order_create(request):
    cart = Cart(request)
    user = request.user
    order = Order.objects.create(user=user)

    for item in cart:
        OrderItem.objects.create(
            order=order,
            product=item["product"],
            price=item["sale_price"],
            quantity=item["quantity"],
        )
    cart.clear()

    # launch asynchronous task
    order_created.delay(order.id)

    # set the order in the session
    request.session["order_id"] = order.id

    # redirect for payment
    return redirect(reverse("payment:process"))


@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "admin/orders/order/detail.html", {"order": order})


@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    html = render_to_string("orders/order/pdf.html", {"order": order})
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"filename=order_{order.id}.pdf"
    weasyprint.HTML(string=html).write_pdf(
        response, stylesheets=[weasyprint.CSS(settings.STATIC_ROOT / "css/pdf.css")]
    )
    return response


# def user_orders(request):
#     user_id = request.user.id
#     orders = Order.objects.filter(user_id=user_id).filter(billing_status=True)
#     return orders
