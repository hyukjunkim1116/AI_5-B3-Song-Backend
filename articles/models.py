from django.db import models


class Article(models.Model):
    title = models.CharField(max_length=50, default="title")
    content = models.TextField()
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="articles",
    )
