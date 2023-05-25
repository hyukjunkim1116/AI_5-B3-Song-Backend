from django.urls import path
from . import views

urlpatterns = [
    path("", views.Articles.as_view()),
    path("<int:article_id>/", views.ArticleDetail.as_view()),
    path("<int:article_id>/photos/", views.ArticlePhotos.as_view()),
    path(
        "<int:article_id>/comments/", views.CommentsView.as_view(), name="comment_view"
    ),
    path(
        "comments/<int:comment_id>/",
        views.CommentsDetailView.as_view(),
        name="comments_detail_view",
    ),
]
