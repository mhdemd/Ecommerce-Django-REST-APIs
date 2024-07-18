from django.urls import path

from .views import OrderPayView, VerifyPayView

app_name = "zarinpal"

urlpatterns = [
    path("pay/", OrderPayView.as_view(), name="pay"),
    path("<str:lang>/verify/", VerifyPayView.as_view(), name="verify"),
]
