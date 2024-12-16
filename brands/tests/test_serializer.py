import pytest

from brands.models import Brand
from brands.serializers import BrandSerializer


@pytest.mark.django_db
class TestBrandSerializer:
    def test_serialize_data(self):
        brand = Brand.objects.create(
            name="Brand A", slug="brand-a", description="Test Desc"
        )
        serializer = BrandSerializer(brand)
        data = serializer.data
        assert data["name"] == "Brand A"
        assert data["slug"] == "brand-a"
        assert data["description"] == "Test Desc"
        assert "created_at" in data
        assert "updated_at" in data

    def test_deserialize_data(self):
        data = {"name": "New Brand", "slug": "new-brand", "description": "Some brand"}
        serializer = BrandSerializer(data=data)
        assert serializer.is_valid() is True
        brand = serializer.save()
        assert brand.name == "New Brand"
        assert brand.slug == "new-brand"
        assert brand.description == "Some brand"
