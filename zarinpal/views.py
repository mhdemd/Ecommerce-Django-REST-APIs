import json

import requests

from account.models import Address
from cart.cart import Cart
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render, reverse
from django.utils.decorators import method_decorator
from django.utils.translation import activate
from django.views import View
from orders.models import Order, OrderItem

# ? sandbox merchant
if settings.SANDBOX:
    sandbox = "sandbox"
else:
    sandbox = "www"


ZP_API_REQUEST = f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
ZP_API_VERIFY = (
    f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
)
ZP_API_STARTPAY = f"https://{sandbox}.zarinpal.com/pg/StartPay/"


@method_decorator(login_required, name="dispatch")
class OrderPayView(View):
    def get(self, request):
        cart = Cart(request)
        if len(cart) != 0:
            amount = float(cart.get_total_price())
            fake_amount = 100
            # add amount to session
            request.session["amount"] = fake_amount

            # Set language based on request or user preferences
            language_code = request.LANGUAGE_CODE

            if language_code == "fa":
                CallbackURL = request.build_absolute_uri(
                    reverse("zarinpal:verify", kwargs={"lang": "fa"})
                )
                activate("fa")
            else:
                CallbackURL = request.build_absolute_uri(
                    reverse("zarinpal:verify", kwargs={"lang": "en"})
                )
                activate("en")

            data = {
                "MerchantID": settings.MERCHANT,
                "Amount": fake_amount,
                "Description": f"مبلغ قابل پرداخت:{amount}",
                "CallbackURL": CallbackURL,
            }

            data = json.dumps(data)

            headers = {
                "content-type": "application/json",
                "content-length": str(len(data)),
            }

            try:
                response = requests.post(
                    ZP_API_REQUEST, data=data, headers=headers, timeout=10
                )

                if response.status_code == 200:
                    response_data = response.json()

                    if response_data["Status"] == 100:
                        url = f"{ZP_API_STARTPAY} {response_data['Authority']}"
                        return redirect(url)
                    else:
                        error_message = response_data.get("ErrorMessage")
                        if error_message:
                            # نمایش پیام خطا به کاربر
                            return HttpResponse(f"خطای پرداخت: {error_message}")
                        else:
                            return HttpResponse("!خطا در پرداخت")
                return HttpResponse("!خطا در برقراری ارتباط")

            except requests.exceptions.Timeout:
                return render(request, "zarinpal/payment_failed.html")
            except requests.exceptions.ConnectionError:
                return render(request, "zarinpal/payment_failed.html")

        else:
            return HttpResponse("!سبد خرید خالی است")


@method_decorator(login_required, name="dispatch")
class VerifyPayView(View):
    def get(self, request, lang):
        authority = request.GET["Authority"]
        amount = float(request.session.get("amount", 0))

        data = {
            "MerchantID": settings.MERCHANT,
            "Amount": amount,
            "Authority": authority,
        }

        data = json.dumps(data)
        headers = {"content-type": "application/json", "content-length": str(len(data))}
        response = requests.post(ZP_API_VERIFY, data=data, headers=headers)

        if response.status_code == 200:
            response = response.json()
            print(response)
            if response["Status"] == 100:
                address_id = request.session["address"]["address_id"]
                shipping_address = Address.objects.get(id=address_id)

                order_key = response.get("RefID")
                order = Order.objects.create(
                    user_id=request.user.id,
                    total_paid=amount,
                    order_key=order_key,
                    payment_option="zarinpal",
                    billing_status=True,
                    shipping_address=shipping_address,
                )

                order_id = order.pk
                cart = Cart(request)

                for item in cart:
                    OrderItem.objects.create(
                        order_id=order_id,
                        product=item["product"],
                        price=item["sale_price"],
                        quantity=item["quantity"],
                    )

                cart.clear()

                return render(request, "zarinpal/payment_successful.html")

            else:
                return render(request, "zarinpal/payment_failed.html")

        return HttpResponse("پرداخت نا موفق")
