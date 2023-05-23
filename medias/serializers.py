from rest_framework import serializers
from .models import Photo, UserPhoto


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = (
            "pk",
            "file",
        )


class UserPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPhoto
        fields = (
            "pk",
            "file",
        )
