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
from users.serializers import UserSerializer, UserUpdateSerializer
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
    
    def get(self, request):
        """유저전체보기"""
        user = User.objects.all()
        serialize = UserSerializer(user, many=True)
        return Response(serialize.data, status=status.HTTP_200_OK)



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
