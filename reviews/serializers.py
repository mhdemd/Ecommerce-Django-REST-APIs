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
            "title",
            "body",
            "rating",
            "product",
            "user",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "user",
            "product",
            "created_at",
            "updated_at",
        ]

    def get_user_name(self, obj):
        """
        Returns the username if show_name is True; otherwise, returns 'Anonymous'
        """
        return obj.user.username if obj.show_name else "Anonymous"


class ReviewVoteSerializer(serializers.ModelSerializer):
    """
    Serializer for voting on reviews
    """

    class Meta:
        model = ReviewVote
        fields = ["id", "user", "review", "is_upvote"]
        read_only_fields = ["user"]


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for creating, updating, and retrieving comments
    """

    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "body",
            "review",
            "user",
            "user_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["review", "user", "created_at", "updated_at"]

    def get_user_name(self, obj):
        """
        Return the username of the commenter
        """
        return obj.user.username if obj.user else "Anonymous"
