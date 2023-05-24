from django.db import models
from users.models import User


class Article(models.Model):
    title = models.CharField(max_length=50, default="title")
    content = models.TextField()
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="articles",
    )
    bookmark = models.ManyToManyField(User, null=True, blank=True, verbose_name="북마크", related_name="bookmarks")


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="comments"
    )
    comment = models.TextField()
    like = models.ManyToManyField(User, null=True, blank=True, verbose_name="좋아요", related_name="like_posts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.comment)
