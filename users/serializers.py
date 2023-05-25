from rest_framework import serializers
from users.models import User


# 유저 생성관련 시리얼라이저
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            "password": {
                "write_only": True, # 작성만 가능하도록 제한! 비밀번호 조회 불가
            },
        }

    def create(self, validated_data):
        user = super().create(validated_data)
        password = user.password
        user.set_password(password) #암호화
        user.save()
        return user
    
    def update(self, user, validated_data):
        user =  super().update(user,validated_data)
        password = user.password
        user.set_password(password) #암호화
        user.save()
        return user
