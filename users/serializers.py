from rest_framework import serializers
from users.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


# 유저 생성관련 시리얼라이저
class UserSerializer(serializers.ModelSerializer):
    like_comments = serializers.SerializerMethodField()
    bookmarks = serializers.SerializerMethodField()
    
    def get_like_comments(self, obj):
        return list(obj.like_comments.values())
    
    def get_bookmarks(self, obj):
        return list(obj.bookmarks.values())
    
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            "password": {
                "write_only": True,  # 작성만 가능하도록 제한! 비밀번호 조회 불가
            },
        }

    def create(self, validated_data):
        user = super().create(validated_data)
        password = user.password
        user.set_password(password)  # 암호화
        user.save()
        return user

    def update(self, user, validated_data):
        user = super().update(user, validated_data)
        password = user.password
        user.set_password(password)  # 암호화
        user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["nickname"] = user.nickname
        return token
