from django import forms
from django.utils.translation import gettext_lazy as _

from .models import ProductAttribute, ProductReview


class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ["review", "rating", "show_name"]
        widgets = {
            "review": forms.Textarea(attrs={"rows": 4, "cols": 40}),
        }
        labels = {
            "review": _("Review"),
            "rating": _("Rating"),
            "show_name": _("Show Name"),
        }


class ProductAttributeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ProductAttributeForm, self).__init__(*args, **kwargs)

        attribute_choices = {}

        all_attributes = ProductAttribute.objects.all().prefetch_related(
            "product_attribute"
        )

        for attribute in all_attributes:
            attribute_values = attribute.product_attribute.all()

            choices = [
                (value.attribute_value, value.attribute_value)
                for value in attribute_values
            ]
            attribute_choices[attribute.name] = choices

        for attr_name, choices in attribute_choices.items():
            self.fields[attr_name] = forms.MultipleChoiceField(
                choices=choices,
                widget=forms.CheckboxSelectMultiple,
                label=_("FILTER BY") + f" {attr_name.upper()}",
                required=False,
            )

        price_choices = [
            ("all", "all"),
            ("$0 - $20", "$0 - $20"),
            ("$20 - $40", "$20 - $40"),
            ("$40 - $60", "$40 - $60"),
            ("$60 - $100", "$60 - $100"),
            ("over $100", "over $100"),
        ]
        self.fields["price"] = forms.ChoiceField(
            choices=price_choices,
            widget=forms.RadioSelect,
            label=_("FILTER BY PRICE"),
            required=False,
        )


class SortingForm(forms.Form):
    SORT_CHOICES = [
        ("Latest", _("Latest")),
        ("Best Rating", _("Best Rating")),
        ("Most Expensive", _("Most Expensive")),
        ("Least Expensive", _("Least Expensive")),
    ]

    sort = forms.ChoiceField(
        choices=SORT_CHOICES,
        widget=forms.Select(attrs={"class": "btn btn-sm btn-light dropdown-toggle"}),
        required=False,
    )
