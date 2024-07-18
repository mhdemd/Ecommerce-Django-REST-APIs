from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from orders.models import Order
from shop.models import Product, ProductInventory, Wishlist

from .forms import RegistrationForm, UserAddressForm, UserEditForm
from .models import Address, UserBase
from .tokens import account_activation_token


# Custom logout function to delete products in the basket before logout
def update_session_data(session_key, updated_data):
    session = Session.objects.get(session_key=session_key)
    session_data = session.get_decoded()
    session_data.update(updated_data)
    session_data["session_key"] = session.session_key
    session.modified = True
    session.save()


def logout_process(session_key):
    try:
        session = Session.objects.get(session_key=session_key)
        session_data = session.get_decoded()
        my_dict = session_data.get("cart", {})

        if my_dict:
            for key, item in my_dict.items():
                product_inventory_id = key
                quantity = item.get("quantity", 0)
                product_inventory = ProductInventory.objects.get(
                    id=product_inventory_id
                )
                product_inventory.stock += quantity
                product_inventory.save()  # به‌روزرسانی موجودی کالا

            # پاک کردن سبد خرید
            my_dict.clear()
            update_session_data(session_key, {"cart": my_dict})
    except Session.DoesNotExist:
        pass  # اگر سشن وجود نداشت، چیزی انجام ندهید


def logout_view(request):
    # شناسه جلسه را دریافت کرده و از تابع logout_process برای به‌روزرسانی موجودی کالاها استفاده می‌کنیم
    session_key = request.session.session_key
    logout_process(session_key)

    # سپس کاربر را از سیستم خارج می‌کنیم
    auth_logout(request)

    return redirect("shop:home")


# Wish List
@login_required
def wishlist(request):
    products = Product.objects.filter(users_wishlist=request.user)
    return render(
        request, "account/dashboard/user_wish_list.html", {"wishlist": products}
    )


@login_required
def add_to_wishlist(request, id):
    product = get_object_or_404(Product, id=id)
    wishlist, created = Wishlist.objects.get_or_create(
        user=request.user, product=product
    )

    if not created:
        wishlist.delete()
        messages.success(
            request, "(" + product.name + ") has been removed from your WishList"
        )
    else:
        messages.success(request, "Added (" + product.name + ") to your WishList")

    return redirect(request.META.get("HTTP_REFERER", "shop:index"))


# Account
@login_required
def dashboard(request):
    # orders = user_orders(request)
    return render(
        request,
        "account/dashboard/dashboard.html",
        {"section": "profile"},
    )


@login_required
def edit_details(request):
    if request.method == "POST":
        user_form = UserEditForm(instance=request.user, data=request.POST)

        if user_form.is_valid():
            user_form.save()
    else:
        user_form = UserEditForm(instance=request.user)

    return render(
        request, "account/dashboard/edit_details.html", {"user_form": user_form}
    )


@login_required
def delete_user(request):
    user = UserBase.objects.get(id=request.user.id)
    user.is_active = False
    user.save()
    logout(request)
    return redirect("account:delete_confirmation")


def account_register(request):
    if request.user.is_authenticated:
        return redirect("account:dashboard")

    if request.method == "POST":
        registerForm = RegistrationForm(request.POST)
        if registerForm.is_valid():
            # Creating an instance of UserBase model (without saving)
            user = registerForm.save(commit=False)
            # Initialize the new instance
            user.email = registerForm.cleaned_data["email"]
            user.set_password(registerForm.cleaned_data["password"])
            user.is_active = False
            # Save instance of UserBase model
            user.save()
            current_site = get_current_site(request)
            subject = "Activate your Account"
            message = render_to_string(
                "account/registration/account_activation_email.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": account_activation_token.make_token(user),
                },
            )
            user.email_user(subject=subject, message=message)
            return render(request, "account/registration/registration_success.html")
    else:
        registerForm = RegistrationForm()
    return render(request, "account/registration/register.html", {"form": registerForm})


def account_activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()  # Decode the bytes to a string
        user = UserBase.objects.get(pk=uid)
    except UserBase.DoesNotExist:
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect("account:dashboard")
    else:
        return render(request, "account/registration/activation_invalid.html")


# Addresses
@login_required
def view_address(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, "account/dashboard/addresses.html", {"addresses": addresses})


@login_required
def add_address(request):
    from_cart = request.GET.get("from_cart", False)

    if request.method == "POST":
        address_form = UserAddressForm(data=request.POST)
        if address_form.is_valid():
            address_instance = address_form.save(commit=False)
            address_instance.user = request.user
            address_instance.save()

            # If default=True, remove the rest of the addresses from the default=True state.
            if address_instance.default:
                Address.objects.filter(user=request.user, default=True).exclude(
                    id=address_instance.id
                ).update(default=False)

            if from_cart:
                return HttpResponseRedirect(reverse("orders:order_create"))
            else:
                return HttpResponseRedirect(reverse("account:addresses"))
    else:
        address_form = UserAddressForm()

    return render(
        request, "account/dashboard/edit_addresses.html", {"form": address_form}
    )


@login_required
def edit_address(request, id):
    if request.method == "POST":
        address = Address.objects.get(pk=id, user=request.user)
        address_form = UserAddressForm(instance=address, data=request.POST)
        if address_form.is_valid():
            address_form = address_form.save(commit=False)

            # If default=True, remove the rest of the addresses from the default=True state.
            if address_form.default:
                Address.objects.filter(user=request.user, default=True).exclude(
                    id=address_form.id
                ).update(default=False)

            address_form.save()
            return HttpResponseRedirect(reverse("account:addresses"))
    else:
        address = Address.objects.get(pk=id, user=request.user)
        address_form = UserAddressForm(instance=address)
    return render(
        request, "account/dashboard/edit_addresses.html", {"form": address_form}
    )


@login_required
def delete_address(request, id):
    # address = Address.objects.filter(pk=id, user=request.user).delete()
    Address.objects.filter(pk=id, user=request.user).delete()

    return redirect("account:addresses")


@login_required
def set_default(request, id, fromcheckout):
    Address.objects.filter(user=request.user, default=True).update(default=False)
    Address.objects.filter(pk=id, user=request.user).update(default=True)
    if fromcheckout != "fromcheckout":
        return redirect("account:addresses")
    else:
        return redirect("checkout:delivery_address")


@login_required
def user_orders(request):
    user_id = request.user.id
    orders = Order.objects.filter(user_id=user_id).filter(billing_status=True)
    return render(request, "account/dashboard/user_orders.html", {"orders": orders})
