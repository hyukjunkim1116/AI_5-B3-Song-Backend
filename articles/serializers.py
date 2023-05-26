from rest_framework import serializers
from medias.serializers import PhotoSerializer
from users.serializers import UserSerializer
from .models import Article, Comment


class ArticleListSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    nickname = serializers.SerializerMethodField()

    def get_nickname(self, obj):
        return obj.owner.nickname

    class Meta:
        model = Article
        fields = (
            "pk",
            "title",
            "owner",
            "nickname",
            "photos",
            "created_at",
        )


class ArticleDetailSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()

    def get_user(self, obj):
        return obj.user.nickname

    def get_like_count(self, obj):
        return obj.like.count()

    class Meta:
        model = Comment
        fields = "__all__"


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("comment",)
