from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.exceptions import (
    NotFound,
    NotAuthenticated,
    ParseError,
    PermissionDenied,
)
from .serializers import (
    ArticleListSerializer,
    ArticleDetailSerializer,
    CommentSerializer,
    CommentCreateSerializer,
    PhotoSerializer,
)
from .models import Article, Comment


class Articles(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        all_articles = Article.objects.all()
        serializer = ArticleListSerializer(
            all_articles,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)

    def post(self, request):
        serializer = ArticleDetailSerializer(
            data=request.data,
        )
        if serializer.is_valid():
            try:
                article = serializer.save(owner=request.user)
                serializer = ArticleDetailSerializer(article)
                return Response(serializer.data)
            except Exception as e:
                print(e)
        else:
            return Response(
                serializer.errors,
                status=HTTP_400_BAD_REQUEST,
            )


class ArticleDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, article_id):
        try:
            return Article.objects.get(pk=article_id)
        except Article.DoesNotExist:
            raise NotFound

    def get(self, request, article_id):
        article = self.get_object(article_id)
        serializer = ArticleDetailSerializer(
            article,
            context={"request": request},
        )
        return Response(serializer.data)

    def put(self, request, article_id):
        article = self.get_object(article_id)

        if article.owner != request.user:
            raise PermissionDenied
        serializer = ArticleDetailSerializer(
            article,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        if serializer.is_valid():
            try:
                article = serializer.save()
                serializer = ArticleDetailSerializer(article)
                return Response(serializer.data)
            except Exception as e:
                print(e)
        else:
            return Response(serializer.errors)

    def delete(self, request, article_id):
        article = self.get_object(article_id)
        if article.owner != request.user:
            raise PermissionDenied
        article.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class ArticlePhotos(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, article_id):
        try:
            return Article.objects.get(pk=article_id)
        except Article.DoesNotExist:
            raise NotFound

    def post(self, request, article_id):
        article = self.get_object(article_id)
        if request.user != article.owner:
            raise PermissionDenied
        serializer = PhotoSerializer(data=request.data)
        if serializer.is_valid():
            photo = serializer.save(article=article)
            serializer = PhotoSerializer(photo)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class CommentsView(APIView):
    def get(self, request, article_id):
        """댓글 보기"""
        articles = get_object_or_404(Article, id=article_id)
        comments = articles.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, article_id):
        """댓글 작성"""
        serializer = CommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, article_id=article_id)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentsDetailView(APIView):
    def put(self, request, comment_id):
        """댓글 수정"""
        comment = get_object_or_404(Comment, id=comment_id)
        if request.user == comment.user:
            serializer = CommentCreateSerializer(comment, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("권한이 없습니다!", status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, comment_id):
        """댓글 삭제"""
        comment = get_object_or_404(Comment, id=comment_id)
        if request.user == comment.user:
            comment.delete()
            return Response("삭제되었습니다!", status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("권한이 없습니다!", status=status.HTTP_403_FORBIDDEN)


class LikeView(APIView):
    def post(self, request, comment_id):
        """댓글 좋아요 누르기"""
        comment = get_object_or_404(Comment, id=comment_id)
        if request.user in comment.like.all():
            comment.like.remove(request.user)
            return Response("dislike", status=status.HTTP_200_OK)
        else:
            comment.like.add(request.user)
            return Response("like", status=status.HTTP_200_OK)
        
        
class BookmarkView(APIView):
    def post(self, request, article_id):
        """게시글 북마크 하기"""
        article = get_object_or_404(Article, id=article_id)
        if request.user in article.bookmark.all():
            article.bookmark.remove(request.user)
            return Response("unbookmark", status=status.HTTP_200_OK)
        else:
            article.bookmark.add(request.user)
            return Response("bookmark", status=status.HTTP_200_OK)