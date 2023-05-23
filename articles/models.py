from django.db import models
from users.models import User


class Article(models.Model):
    title = models.CharField("제목", max_length=100)
    content = models.TextField("내용")
    created_at = models.DateTimeField("생성시간", auto_now_add=True)
    updated_at = models.DateTimeField("마지막 수정시간", auto_now=True)

    def __str__(self):
        return str(self.title)

    def like_count(self):
        return self.like.count()


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
