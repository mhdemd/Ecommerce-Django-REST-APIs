from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from products.models import Product


class CartStatus(models.TextChoices):
    ACTIVE = "active", _("Active")
    CHECKOUT = "checkout", _("Checkout")
    COMPLETED = "completed", _("Completed")
    CANCELED = "canceled", _("Canceled")
