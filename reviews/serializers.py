from rest_framework import serializers

from .models import Comment, Review, ReviewVote


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for creating, updating, and retrieving reviews
    """

    class Meta:
        model = Review
        fields = [
            "id",
            "user",
            "user_name",
            "product",
            "title",
            "body",
            "rating",
            "is_approved",
            "show_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "is_approved", "created_at", "updated_at"]

    def get_user_name(self, obj):
        """
        Returns the username if show_name is True; otherwise, returns 'Anonymous'
        """
        return obj.user.username if obj.show_name else "Anonymous"
