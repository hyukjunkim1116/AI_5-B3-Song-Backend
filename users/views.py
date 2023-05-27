import requests
from django.shortcuts import redirect
from my_settings import (
    KAKAO_REST_API_KEY,
    GOOGLE_API_KEY,
    NAVER_API_KEY,
    NAVER_SECRET_KEY,
)
from medias.serializers import PhotoSerializer, UserPhotoSerializer
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.generics import get_object_or_404
from users.serializers import CustomTokenObtainPairSerializer, UserSerializer, UserProfileSerializer
from users.models import User
from articles.models import Article, Comment
from articles.serializers import ArticleListSerializer, CommentSerializer
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
        serializer = UserProfileSerializer(user, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserPhotoView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise NotFound

    def post(self, request, user_id):
        """유저 프로필 사진 올리기"""
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
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, user_id):
        """유저 프로필 수정"""
        user = get_object_or_404(User, id=user_id)
        # 현재유저와 수정하려는 유저가 일치한다면
        if request.user.id == user_id:
            serializer = UserSerializer(user, data=request.data, partial=True)
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
                return Response(
                    f"{user.email}이 휴면계정이 되었습니다!", status=status.HTTP_204_NO_CONTENT
                )
            else:
                user.is_active = True
                user.save()
                return Response(
                    f"{user.email}계정이 활성화 되었습니다!", status=status.HTTP_204_NO_CONTENT
                )
        else:
            return Response("권한이 없습니다!", status=status.HTTP_403_FORBIDDEN)


class ProfileAticlesView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, user_id):
        """유저 프로필 게시글 조회"""
        user_articles = Article.objects.filter(owner_id=user_id)
        serializer = ArticleListSerializer(
            user_articles,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileLikesView(APIView):
    def get(self, request, user_id):
        """유저 프로필 좋아요 조회"""
        comments = Comment.objects.filter(like=user_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileBookmarksView(APIView):
    def get(self, request, user_id):
        """유저 프로필 북마크 조회"""
        user_articles = Article.objects.filter(bookmark=user_id)
        serializer = ArticleListSerializer(user_articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowView(APIView):
    def get(self, request, user_id):
        """유저 팔로우한 유저들 조회"""
        follow = User.objects.filter(followings=user_id)
        serializer = UserSerializer(follow, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, user_id):
        """유저 팔로잉 누르기"""
        you = get_object_or_404(User, id=user_id)
        me = request.user
        if request.user.id != user_id:
            if me in you.followers.all():
                you.followers.remove(me)
                return Response("unfollow", status=status.HTTP_200_OK)
            else:
                you.followers.add(me)
                return Response("follow", status=status.HTTP_200_OK)
        else:
            return Response("자신을 팔로우 할 수 없습니다!", status=status.HTTP_403_FORBIDDEN)


############################ 소셜 로그인 ############################
# 각각의 get 메소드는 프론트에 api key를 전달하기 위한 메소드입니다.
# 각각의 post 메소드는 프론트에서 받은 데이터로 액세스 토큰과 유저 데이터를 받아와서 SocialLogin함수를 호출합니다.
# SocialLogin 함수는 해당 정보를 바탕으로 유저가 있다면 로그인하고, 없다면 유저를 생성합니다.
class KakaoLogin(APIView):
    """카카오 소셜 로그인"""

    def get(self, request):
        return Response(KAKAO_REST_API_KEY, status=status.HTTP_200_OK)

    def post(self, request):
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
        data = {
            "avatar": user_data.get("properties").get("profile_image"),
            "email": user_data.get("kakao_account").get("email"),
            "nickname": user_data.get("properties").get("nickname"),
            "gender": user_data.get("properties").get("gender"),
            "login_type": "kakao",
        }
        return SocialLogin(**data)


class GoogleLogin(APIView):
    """구글 소셜 로그인"""

    def get(self, request):
        return Response(GOOGLE_API_KEY, status=status.HTTP_200_OK)

    def post(self, request):
        access_token = request.data["access_token"]
        user_data = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_data = user_data.json()
        data = {
            "avatar": user_data.get("picture"),
            "email": user_data.get("email"),
            "nickname": user_data.get("name"),
            "login_type": "google",
        }
        return SocialLogin(**data)


class NaverLogin(APIView):
    """네이버 소셜 로그인"""

    def get(self, request):
        return Response(NAVER_API_KEY, status=status.HTTP_200_OK)

    def post(self, request):
        code = request.data.get("naver_code")
        state = request.data.get("state")
        access_token = requests.post(
            f"https://nid.naver.com/oauth2.0/token?grant_type=authorization_code&code={code}&client_id={NAVER_API_KEY}&client_secret={NAVER_SECRET_KEY}&state={state}",
            headers={"Accept": "application/json"},
        )
        access_token = access_token.json().get("access_token")
        user_data = requests.get(
            "https://openapi.naver.com/v1/nid/me",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
        )
        user_data = user_data.json().get("response")
        data = {
            "avatar": user_data.get("profile_image"),
            "email": user_data.get("email"),
            "nickname": user_data.get("nickname"),
            "login_type": "naver",
        }
        return SocialLogin(**data)


def SocialLogin(**kwargs):
    """소셜 로그인, 회원가입"""
    # 각각 소셜 로그인에서 email, nickname, login_type등을 받아옴!!
    data = {k: v for k, v in kwargs.items() if v is not None}
    # none인 값들은 빼줌
    email = data.get("email")
    login_type = data.get("login_type")
    # 그 중 email이 없으면 회원가입이 불가능하므로
    # 프론트에서 메시지를 띄워주고, 다시 로그인 페이지로 이동시키기
    if not email:
        return Response(
            {"error": "해당 계정에 email정보가 없습니다."}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        user = User.objects.get(email=email)
        # 로그인 타입까지 같으면, 토큰 발행해서 프론트로 보내주기
        if login_type == user.login_type:
            refresh = RefreshToken.for_user(user)
            access_token = CustomTokenObtainPairSerializer.get_token(user)
            return Response(
                {"refresh": str(refresh), "access": str(access_token.access_token)},
                status=status.HTTP_200_OK,
            )
        # 유저의 다른 소셜계정으로 로그인한 유저라면, 해당 로그인 타입을 보내줌.
        # (프론트에서 "{login_type}으로 로그인한 계정이 있습니다!" alert 띄워주기)
        else:
            return Response(
                {"error": f"{user.login_type}으로 이미 가입된 계정이 있습니다!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    # 유저가 존재하지 않는다면 회원가입시키기
    except User.DoesNotExist:
        new_user = User.objects.create(**data)
        # pw는 사용불가로 지정
        new_user.set_unusable_password()
        new_user.save()
        # 이후 토큰 발급해서 프론트로
        refresh = RefreshToken.for_user(new_user)
        access_token = CustomTokenObtainPairSerializer.get_token(new_user)
        return Response(
            {"refresh": str(refresh), "access": str(access_token.access_token)},
            status=status.HTTP_200_OK,
        )
