from django.urls import path
from . import views

urlpatterns = [
    path("", views.Articles.as_view()),
    path("<int:article_id>/", views.ArticleDetail.as_view()),
    path("<int:article_id>/photos/", views.ArticlePhotos.as_view()),
    path("comments/", views.CommentsView.as_view(), name="main_comment_view"),
    path(
        "<int:article_id>/comments/", views.CommentsView.as_view(), name="comment_view"
    ),
    path(
        "comments/<int:comment_id>/",
        views.CommentsDetailView.as_view(),
        name="comments_detail_view",
    ),
    path("like/<int:comment_id>/", views.LikeView.as_view(), name="like_view"),
    path(
        "bookmark/<int:article_id>/", views.BookmarkView.as_view(), name="bookmark_view"
    ),
    path("search/<str:query>/", views.SearchView.as_view(), name="search_view"),
]
