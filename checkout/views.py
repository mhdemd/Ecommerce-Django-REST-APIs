import json

from account.models import Address
from cart.cart import Cart
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from orders.models import Order, OrderItem

from .models import DeliveryOptions


@login_required
def deliverychoices(request):
    # Extend Cart Expiry Time
    user_cart = Cart(request)
    first_item_expiry = user_cart.get_latest_expiry_time()

    if first_item_expiry:
        new_expiry = first_item_expiry.replace(tzinfo=None)  # Convert to naive datetime
        new_expiry += timezone.timedelta(minutes=45)  # Add 45 minutes

        # Limit expiry to maximum of 60 minutes from now
        max_expiry = timezone.now() + timezone.timedelta(minutes=45)
        if new_expiry > max_expiry:
            new_expiry = max_expiry

        first_item_key = list(user_cart.cart.keys())[0]
        user_cart.cart[first_item_key]["expiry_date"] = new_expiry.isoformat()
        user_cart.save()

    deliveryoptions = DeliveryOptions.objects.filter(is_active=True)

    if "purchase" in request.session:
        del request.session["purchase"]

    return render(
        request, "checkout/delivery_choices.html", {"deliveryoptions": deliveryoptions}
    )


@login_required
def cart_update_delivery(request):
    cart = Cart(request)
    if request.POST.get("action") == "post":
        delivery_option = int(request.POST.get("deliveryoption"))
        delivery_type = DeliveryOptions.objects.get(id=delivery_option)
        updated_total_price = cart.cart_update_delivery(delivery_type.delivery_price)

        session = request.session
        if "purchase" not in request.session:
            session["purchase"] = {
                "delivery_id": delivery_type.id,
            }
        else:
            session["purchase"]["delivery_id"] = delivery_type.id
            session.modified = True

        response = JsonResponse(
            {
                "total": updated_total_price,
                "delivery_price": delivery_type.delivery_price,
            }
        )
        return response


@login_required
def delivery_address(request):
    session = request.session
    if "purchase" not in request.session:
        messages.success(request, "Please select delivery option")
        return HttpResponseRedirect(request.META["HTTP_REFERER"])

    addresses = Address.objects.filter(user=request.user).order_by("-default")

    if len(addresses) > 0:
        if "address" not in request.session:
            session["address"] = {"address_id": str(addresses[0].id)}
        else:
            session["address"]["address_id"] = str(addresses[0].id)
            session.modified = True

    return render(request, "checkout/delivery_address.html", {"addresses": addresses})


@login_required
def payment_selection(request):
    if "address" not in request.session:
        messages.success(request, "Please select address option")
        return HttpResponseRedirect(request.META["HTTP_REFERER"])

    return render(request, "checkout/payment_selection.html", {})


####
# PayPay
####
from paypalcheckoutsdk.orders import OrdersGetRequest

from .paypal import PayPalClient


@login_required
def payment_complete(request):
    PPClient = PayPalClient()

    body = json.loads(request.body)
    data = body["orderID"]
    user_id = request.user.id

    requestorder = OrdersGetRequest(data)
    response = PPClient.client.execute(requestorder)

    # total_paid = response.result.purchase_units[0].amount.value
    address_id = request.session["address"]["address_id"]
    shipping_address = Address.objects.get(id=address_id)

    cart = Cart(request)
    order = Order.objects.create(
        user_id=user_id,
        total_paid=response.result.purchase_units[0].amount.value,
        order_key=response.result.id,
        payment_option="paypal",
        billing_status=True,
        shipping_address=shipping_address,
    )
    order_id = order.pk

    for item in cart:
        OrderItem.objects.create(
            order_id=order_id,
            product=item["product"],
            price=item["sale_price"],
            quantity=item["quantity"],
        )

    return JsonResponse("Payment completed!", safe=False)


@login_required
def payment_successful(request):
    cart = Cart(request)
    cart.clear()
    return render(request, "checkout/payment_successful.html", {})
