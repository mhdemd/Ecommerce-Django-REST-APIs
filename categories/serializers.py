from rest_framework import serializers

from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model.
    Includes all relevant fields for both user and admin views.
    """

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "parent", "is_active"]
        read_only_fields = ["id"]
