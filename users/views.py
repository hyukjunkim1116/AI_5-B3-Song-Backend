import requests
from django.shortcuts import redirect
from my_settings import KAKAO_REST_API_KEY
from medias.serializers import PhotoSerializer, UserPhotoSerializer
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.generics import get_object_or_404
from users.serializers import UserSerializer
from users.models import User
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken


class UserView(APIView):
    def post(self, request):
        """회원가입"""
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "가입완료!"}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"message": f"${serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST
            )


class UserPhotoView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise NotFound

    def post(self, request, user_id):
        user = self.get_object(user_id)
        if request.user != user:
            raise PermissionDenied
        serializer = UserPhotoSerializer(data=request.data)
        if serializer.is_valid():
            avatar = serializer.save()
            serializer = UserPhotoSerializer(avatar)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class ProfileView(APIView):
    def get(self, request, user_id):
        """유저 프로필 조회"""
        user = get_object_or_404(User, id=user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class KakaoLogin(APIView):
    def get(self, request):
        return Response(KAKAO_REST_API_KEY, status=status.HTTP_200_OK)

    def post(self, request):
        """카카오 로그인"""
        auth_code = request.data.get("code")
        kakao_token_api = "https://kauth.kakao.com/oauth/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": KAKAO_REST_API_KEY,
            "redirect_uri": "http://127.0.0.1:5500/index.html",
            "code": auth_code,
        }
        kakao_token = requests.post(
            kakao_token_api,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=data,
        )
        access_token = kakao_token.json().get("access_token")
        user_data = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
            },
        )
        user_data = user_data.json()
        kakao_email = user_data.get("kakao_account")["email"]
        kakao_nickname = user_data.get("properties")["nickname"]
        kakao_profile_image = user_data.get("properties")["profile_image"]

        try:
            user = User.objects.get(email=kakao_email)
            if user.login_type == "kakao":
                refresh = RefreshToken.for_user(user)
                return Response(
                    {"refresh": str(refresh), "access": str(refresh.access_token)},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(user.login_type, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            new_user = User.objects.create(
                avatar=kakao_profile_image,
                nickname=kakao_nickname,
                email=kakao_email,
                login_type="kakao",
            )
            new_user.set_unusable_password()
            new_user.save()
            return Response(user_data, status=status.HTTP_200_OK)
