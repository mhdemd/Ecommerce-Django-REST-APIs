from account.models import Address, UserBase
from django.db import models
from django.utils.translation import gettext_lazy as _
from shop.models import Product


class Order(models.Model):
    user = models.ForeignKey(UserBase, related_name="user", on_delete=models.CASCADE)
    shipping_address = models.ForeignKey(Address, on_delete=models.PROTECT)
    created = models.DateTimeField(_("created"), auto_now_add=True)
    updated = models.DateTimeField(_("updated"), auto_now=True)
    total_paid = models.DecimalField(_("total paid"), max_digits=5, decimal_places=2)
    order_key = models.CharField(_("order key"), max_length=200)
    payment_option = models.CharField(_("payment option"), max_length=200, blank=True)
    billing_status = models.BooleanField(_("billing status"), default=False)

    class Meta:
        verbose_name = _("order")
        verbose_name_plural = _("orders")
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["-created"]),
        ]

    def __str__(self):
        return _("Order") + " " + str(self.id)

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, related_name="order_items", on_delete=models.CASCADE
    )
    price = models.DecimalField(_("price"), max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(_("quantity"), default=1)

    class Meta:
        verbose_name = _("order item")
        verbose_name_plural = _("order items")

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity
