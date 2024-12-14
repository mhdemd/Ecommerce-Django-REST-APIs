from rest_framework import serializers

from .models import Category


class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class CategorySerializer(serializers.ModelSerializer):
    children = RecursiveField(many=True, read_only=True)
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "is_active",
            "parent",
            "children",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "children", "created_at", "updated_at"]
