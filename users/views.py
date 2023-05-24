from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, PermissionDenied
from medias.serializers import PhotoSerializer, UserPhotoSerializer
from rest_framework.generics import get_object_or_404
from users.models import User
from users.serializers import UserSerializer, UserUpdateSerializer


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

    def put(self, request, user_id):
        """유저 프로필 수정"""
        user = get_object_or_404(User, id=user_id)
        # 현재유저와 수정하려는 유저가 일치한다면
        if request.user.id == user_id:
            serializer = UserUpdateSerializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("권한이 없습니다!", status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, user_id):
        """유저 삭제"""
        user = get_object_or_404(User, id=user_id)
        # 현재유저와 삭제하려는 유저가 일치한다면
        if request.user.id == user_id:
            user.delete()
            return Response("삭제되었습니다!", status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("권한이 없습니다!", status=status.HTTP_403_FORBIDDEN)

    def post(self, request, user_id):
        """유저 비활성화(휴면계정화) 관리자 전용"""
        user = get_object_or_404(User, id=user_id)
        # 현재유저가 관리자 유저라면
        if request.user.is_admin:
            if user.is_active:
                user.is_active = False
                user.save()
                return Response(f"{user.email}이 휴면계정이 되었습니다!", status=status.HTTP_204_NO_CONTENT)
            else:
                user.is_active = True
                user.save()
                return Response(f"{user.email}계정이 활성화 되었습니다!", status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("권한이 없습니다!", status=status.HTTP_403_FORBIDDEN)