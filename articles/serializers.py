from rest_framework import serializers
from medias.serializers import PhotoSerializer
from .models import Article


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
