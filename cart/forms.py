from django import forms
from django.utils.translation import gettext_lazy as _

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 100)]


class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(
        choices=PRODUCT_QUANTITY_CHOICES, coerce=int, label=_("Quantity")
    )
    override = forms.BooleanField(
        required=False, initial=False, widget=forms.HiddenInput
    )

    def __init__(
        self,
        product,
        cart_quantities_dict=None,
        sale_price=None,
        variety_choices=None,
        variety_name=None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.product = product
        self.cart_quantities_dict = cart_quantities_dict

        self.fields["variety"] = forms.ChoiceField(
            label=str(variety_name).capitalize(),
            widget=forms.RadioSelect(attrs={"onchange": "updatePrice()"}),
            choices=variety_choices,
            initial=variety_choices[0][0] if variety_choices else None,
            required=True,
        )

        # Add a data-sale-price attribute to each radio button
        for variety_id, price in sale_price.items():
            self.fields["variety"].widget.attrs[f"data-sale-price-{variety_id}"] = price

    def clean(self):
        cleaned_data = super().clean()
        override = cleaned_data.get("override")
        quantity = cleaned_data.get("quantity")
        variety_id = cleaned_data.get("variety")

        cart_quantities_dict = self.cart_quantities_dict

        pre_quantity = 0
        if override:
            pre_quantity = cart_quantities_dict[variety_id]

        selected_inventory = self.product.product_inventory.only("stock").get(
            id=variety_id
        )
        selected_inventory_stock = selected_inventory.stock

        if quantity > selected_inventory_stock + pre_quantity:
            attribute_values = selected_inventory.attribute_values
            error_msg = _(
                "Now the maximum available quantity for the selected {} is {}."
            ).format(attribute_values, selected_inventory_stock)

            self.add_error("quantity", error_msg)

        return cleaned_data
