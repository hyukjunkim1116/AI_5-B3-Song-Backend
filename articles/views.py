from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.status import (
    HTTP_204_NO_CONTENT,
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
)
from rest_framework.exceptions import (
    NotFound,
    PermissionDenied,
)
from .serializers import (
    ArticleListSerializer,
    ArticleDetailSerializer,
    CommentSerializer,
    CommentCreateSerializer,
    PhotoSerializer,
)

from django.db.models.query_utils import Q

from django.http import JsonResponse
from .models import Article, Comment

from django.conf import settings
import requests
from .openai_utility import recommend_music_and_link

import urllib


class Articles(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def handleError(self, request, exception):
        """
        Handle the error and return the proper Response.
        """
        return JsonResponse({"detail": str(exception)}, status=500)

    def get(self, request):
        """전체 게시글 목록 보기"""
        all_articles = Article.objects.all().order_by("-created_at")
        serializer = ArticleListSerializer(
            all_articles,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)

    # AI 사용하지 않는 게시글 작성 함수
    # def post(self, request):
    #     """게시글 작성하기"""
    #     serializer = ArticleDetailSerializer(
    #         data=request.data,
    #         # context={"request": request},
    #     )
    #     if serializer.is_valid():
    #         try:
    #             article = serializer.save(owner=request.user)
    #             serializer = ArticleDetailSerializer(article)
    #             return Response(serializer.data)
    #         except Exception as e:
    #             return Response(e, status=status.HTTP_400_BAD_REQUEST)
    #     else:
    #         return Response(
    #             serializer.errors,
    #             status=HTTP_400_BAD_REQUEST,
    # )

    def post(self, request):
        serializer = ArticleDetailSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        try:
            article = serializer.save(owner=request.user)
            content = request.data["content"]

            recommendation, youtube_link = recommend_music_and_link(content)
            link_comment = f"들려주신 사연을 듣고 어울릴만한 음악을 찾았어요! \n {youtube_link}"
            serializer = ArticleDetailSerializer(article)

            url = f"{settings.API_BASE_URL}/articles/{article.id}/comments/"
            data = {"comment": link_comment}
            headers = {"Authorization": f"Bearer {request.auth.__str__()}"}
            response = requests.post(url, json=data, headers=headers)
            if response.status_code != status.HTTP_200_OK:
                return Response(
                    "포스팅 오류",
                    response.status_code,
                )

            return Response(serializer.data)
        except Exception as e:
            return JsonResponse({"detail": str(e)}, status=500)


class ArticleDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, article_id):
        try:
            return Article.objects.get(pk=article_id)
        except Article.DoesNotExist:
            raise NotFound

    def get(self, request, article_id):
        """상세 게시글 보기"""
        article = self.get_object(article_id)
        serializer = ArticleDetailSerializer(
            article,
            context={"request": request},
        )
        return Response(serializer.data)

    def put(self, request, article_id):
        """게시글 수정하기"""
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
                return Response(e, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors)

    def delete(self, request, article_id):
        """게시글 삭제하기"""
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
        """게시글 사진 올리기"""
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
    def get(self, request, article_id=None):
        """댓글 보기"""
        if article_id:
            articles = get_object_or_404(Article, id=article_id)
            comments = articles.comments.all()
        else:
            comments = Comment.objects.all()
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
    def get(self, request, comment_id):
        """특정 댓글 조회"""
        comment = get_object_or_404(Comment, id=comment_id)
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)

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


class SearchView(APIView):
    def get(self, request, query):
        """검색하기

        제목이나 내용에 입력한 검색어가 포함되어 있는 게시글들을 가져옴"""
        decoded_query = urllib.parse.unquote(query)
        articles = Article.objects.filter(
            Q(title__contains=decoded_query) | Q(content__contains=decoded_query)
        )
        serializer = ArticleListSerializer(articles, many=True)
        if articles:
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response("검색 결과가 없습니다", status=status.HTTP_204_NO_CONTENT)
