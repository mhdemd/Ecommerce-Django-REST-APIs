from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey


class Brand(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name=_("Brand Name"),
        help_text=_("Required, unique, max 255 characters"),
        unique=True,
        null=False,
        blank=False,
    )
    description = models.TextField(
        verbose_name=_("Brand Description"),
        help_text=_("Optional"),
        null=True,
        blank=True,
    )
    logo = models.ImageField(
        upload_to="brand_logos/",
        verbose_name=_("Brand Logo"),
        help_text=_("Optional"),
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name
