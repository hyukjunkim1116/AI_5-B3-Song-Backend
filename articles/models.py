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


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="comments"
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.comment)
