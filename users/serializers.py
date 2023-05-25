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


# 유저 수정관련 시리얼라이저
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            "password": {
                "write_only": True, # 작성만 가능하도록 제한! 비밀번호 조회 불가
            },
            "email": {
                "read_only": True, # 조회만 가능하도록 제한! 이메일 수정 불가
            },
        }

    def update(self, user, validated_data):
        user.nickname = validated_data.get('nickname', user.nickname)
        user.genre = validated_data.get('genre', user.genre)
        user.age = validated_data.get('age', user.age)
        user.gender = validated_data.get('gender', user.gender)
        password = user.password
        user.set_password(password)
        user.save()
        return user