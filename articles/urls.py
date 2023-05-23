from django.urls import path
from . import views

urlpatterns = [
    path("", views.Articles.as_view()),
    path("<int:article_id>", views.ArticleDetail.as_view()),
    path("<int:article_id>/photos", views.ArticlePhotos.as_view()),
]
