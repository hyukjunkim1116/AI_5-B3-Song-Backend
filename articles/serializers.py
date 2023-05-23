from rest_framework import serializers
from medias.serializers import PhotoSerializer
from .models import Article, Comment


class ArticleListSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = (
            "pk",
            "title",
            "photos",
        )


class ArticleDetailSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        exclude = ("owner",)


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        return obj.user.email

    class Meta:
        model = Comment
        exclude = ("article",)


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("comment",)
