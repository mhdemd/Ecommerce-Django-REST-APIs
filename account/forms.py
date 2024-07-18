from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.utils.translation import gettext_lazy as _

from .models import Address, UserBase


class UserAddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            "recipient_name",
            "recipient_phone",
            "country",
            "address_line",
            "address_line2",
            "town_city",
            "postcode",
            "default",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ترجمه برای برچسب‌ها و placeholder ها
        self.fields["recipient_name"].label = _(
            "Recipient Full Name"
        )  # ترجمه برای برچسب نام گیرنده
        self.fields["recipient_phone"].label = _(
            "Phone Number"
        )  # ترجمه برای برچسب شماره تلفن
        self.fields["country"].label = _("Country")  # ترجمه برای برچسب کشور
        self.fields["address_line"].label = _(
            "Address Line 1"
        )  # ترجمه برای برچسب آدرس خط 1
        self.fields["address_line2"].label = _(
            "Address Line 2"
        )  # ترجمه برای برچسب آدرس خط 2
        self.fields["town_city"].label = _(
            "Town/City/State"
        )  # ترجمه برای برچسب شهر/شهرستان/استان
        self.fields["postcode"].label = _("Postcode")  # ترجمه برای برچسب کد پستی


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label=_("Username"),  # ترجمه برای برچسب نام کاربری
        widget=forms.TextInput(
            attrs={
                "class": "form-control mb-3",
                "placeholder": _(
                    "Username"
                ),  # ترجمه برای متن نام کاربری در placeholder
                "id": "login-username",
            }
        ),
    )
    password = forms.CharField(
        label=_("Password"),  # ترجمه برای برچسب رمز عبور
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Password"),  # ترجمه برای متن رمز عبور در placeholder
                "id": "login-pwd",
            }
        ),
    )


class RegistrationForm(forms.ModelForm):
    first_name = forms.CharField(
        label=_("First Name"),  # ترجمه برای برچسب نام
        min_length=4,
        max_length=50,
        help_text=_("Required"),  # ترجمه برای متن راهنما
    )
    last_name = forms.CharField(
        label=_("Last Name"),  # ترجمه برای برچسب نام خانوادگی
        min_length=4,
        max_length=50,
        help_text=_("Required"),  # ترجمه برای متن راهنما
    )
    email = forms.EmailField(
        max_length=100,
        help_text=_("Required"),  # ترجمه برای متن راهنما
        error_messages={
            "required": _("Sorry, you will need an email")
        },  # ترجمه برای پیام خطا
    )
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Repeat password"), widget=forms.PasswordInput)

    class Meta:
        model = UserBase
        fields = (
            "first_name",
            "last_name",
            "email",
        )

    def clean_password2(self):
        cd = self.cleaned_data
        if cd["password"] != cd["password2"]:
            raise forms.ValidationError(
                _("Passwords do not match.")
            )  # ترجمه برای پیام خطا
        return cd["password2"]

    def clean_email(self):
        email = self.cleaned_data["email"]
        if UserBase.objects.filter(email=email).exists():
            raise forms.ValidationError(
                _("Please use another Email, that is already taken")
            )  # ترجمه برای پیام خطا
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].widget.attrs.update(
            {
                "class": "form-control mb-3",
                "placeholder": _("First Name"),
            }  # ترجمه برای placeholder
        )
        self.fields["last_name"].widget.attrs.update(
            {
                "class": "form-control mb-3",
                "placeholder": _("Last Name"),
            }  # ترجمه برای placeholder
        )
        self.fields["email"].widget.attrs.update(
            {
                "class": "form-control mb-3",
                "placeholder": _("E-mail"),  # ترجمه برای placeholder
                "name": "email",
                "id": "id_email",
            }
        )
        self.fields["password"].widget.attrs.update(
            {
                "class": "form-control mb-3",
                "placeholder": _("Password"),
            }  # ترجمه برای placeholder
        )
        self.fields["password2"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": _("Repeat Password"),
            }  # ترجمه برای placeholder
        )


class PwdResetForm(PasswordResetForm):
    email = forms.EmailField(
        label=_("Email"),  # ترجمه برای برچسب ایمیل
        max_length=254,
        widget=forms.TextInput(
            attrs={
                "class": "form-control mb-3",
                "placeholder": _("Email"),  # ترجمه برای placeholder
                "id": "form-email",
            }
        ),
    )

    def clean_email(self):
        email = self.cleaned_data["email"]
        u = UserBase.objects.filter(email=email)
        if not u:
            raise forms.ValidationError(
                _("Unfortunately we cannot find that email address")
            )  # ترجمه برای پیام خطا
        return email


class PwdResetConfirmForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label=_("New password"),  # ترجمه برای برچسب رمز عبور جدید
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control mb-3",
                "placeholder": _("New Password"),  # ترجمه برای placeholder
                "id": "form-newpass",
            }
        ),
    )
    new_password2 = forms.CharField(
        label=_("Repeat password"),  # ترجمه برای برچسب تکرار رمز عبور
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control mb-3",
                "placeholder": _("Repeat Password"),  # ترجمه برای placeholder
                "id": "form-new-pass2",
            }
        ),
    )


class UserEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control mb-3"

            # ترجمه برای برچسب‌ها و placeholder ها
            if field_name == "email":
                field.label = _("Email")  # ترجمه برای برچسب ایمیل
                field.widget.attrs["placeholder"] = _("Email")  # ترجمه برای placeholder
                field.widget.attrs["readonly"] = True
            elif field_name == "first_name":
                field.label = _("First Name")  # ترجمه برای برچسب نام
                field.widget.attrs["placeholder"] = _(
                    "First Name"
                )  # ترجمه برای placeholder
            elif field_name == "last_name":
                field.label = _("Last Name")  # ترجمه برای برچسب نام خانوادگی
                field.widget.attrs["placeholder"] = _(
                    "Last Name"
                )  # ترجمه برای placeholder
            elif field_name == "mobile":
                field.label = _("Mobile")  # ترجمه برای برچسب موبایل
                field.widget.attrs["placeholder"] = _(
                    "Mobile"
                )  # ترجمه برای placeholder

    class Meta:
        model = UserBase
        fields = ["email", "first_name", "last_name", "mobile"]
