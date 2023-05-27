from django.db import models
from users.models import User
import re


class Article(models.Model):
    title = models.CharField(max_length=50, default="title")
    content = models.TextField()
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="articles",
    )
    bookmark = models.ManyToManyField(
        User, blank=True, verbose_name="북마크", related_name="bookmarks"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.title)

    def total_comments(self):
        return self.comments.count()

    def total_bookmarks(self):
        return self.bookmark.count()

    def comments_url_list(self):
        comments = self.comments.all()
        comment_url_content = ""
        url_regex = r"(https?:\/\/)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&\/\/=]*)"
        reg = re.compile(url_regex)

        for comment in comments:
            res = reg.search(comment.comment)
            if res:
                indexes = res.span()
                comment_url_txt = comment.comment[indexes[0] : indexes[1]]
                article_id = comment.article.pk
                comment_id = comment.id
                comment_user = comment.user
                is_AI = False
                if comment == comments[0]:
                    is_AI = True
                comment_url_content += f"게시글 id : {article_id} / 댓글 id : {comment_id} / 댓글 유저 이름 : {comment_user} / 댓글 유저는 ai인가? : {is_AI} / 댓글 내용 URL : {comment_url_txt}\n\n"
        if comment_url_content == "":
            return "Url이 포함된 댓글이 없습니다!"
        else:
            return comment_url_content


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="comments"
    )
    comment = models.TextField()
    like = models.ManyToManyField(
        User, blank=True, verbose_name="좋아요", related_name="like_comments"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.comment)
