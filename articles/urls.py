from django.urls import path
from articles import views

urlpatterns = [
    path(
        "<int:article_id>/comments/", views.CommentsView.as_view(), name="comment_view"
    ),
    path(
        "<int:article_id>/comments/<int:comment_id>/",
        views.CommentsDetailView.as_view(),
        name="comments_detail_view",
    ),
]
