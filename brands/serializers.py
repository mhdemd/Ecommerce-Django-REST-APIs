from rest_framework import serializers

from .models import Brand


class BrandSerializer(serializers.ModelSerializer):
    """
    Serializer for brand model
    """

    class Meta:
        model = Brand
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "logo",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]
