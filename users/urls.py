from django.urls import path
from users import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("", views.UserView.as_view(), name="user_all_view"),
    path("signup/", views.UserView.as_view(), name="user_view"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/<int:user_id>/", views.ProfileView.as_view(), name="profile_view"),
    path("profile/<int:user_id>/myarticles/", views.ProfileAticlesView.as_view(), name="profile_myarticles"),
    path("profile/<int:user_id>/likes/", views.ProfileLikesView.as_view(), name="profile_likes"),
    path("profile/<int:user_id>/bookmarks/", views.ProfileBookmarksView.as_view(), name="profile_bookmarks"),
    path("<int:user_id>/photos/", views.UserPhotoView.as_view()),
    path("kakao/", views.KakaoLogin.as_view(), name="kakao_login"),
]
