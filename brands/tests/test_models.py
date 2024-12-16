import pytest
from django.core.exceptions import ValidationError

from brands.models import Brand


@pytest.mark.django_db
class TestBrandModel:
    def test_create_brand(self):
        brand = Brand.objects.create(name="Brand A", slug="brand-a")
        assert brand.id is not None
        assert brand.name == "Brand A"
        assert brand.slug == "brand-a"
        assert brand.description is None
        assert brand.logo == ""
        assert brand.created_at is not None
        assert brand.updated_at is not None

    def test_unique_name(self):
        Brand.objects.create(name="Brand A", slug="brand-a")
        with pytest.raises(ValidationError):
            brand2 = Brand(name="Brand A", slug="brand-a-2")
            brand2.full_clean()

    def test_unique_slug(self):
        Brand.objects.create(name="Brand A", slug="brand-a")
        with pytest.raises(ValidationError):
            brand2 = Brand(name="Brand B", slug="brand-a")
            brand2.full_clean()

    def test_str_representation(self):
        brand = Brand.objects.create(name="Brand Test", slug="brand-test")
        assert str(brand) == "Brand Test"
