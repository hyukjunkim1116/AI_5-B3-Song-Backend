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
from .serializers import ArticleListSerializer, ArticleDetailSerializer
from .models import Article
from medias.serializers import PhotoSerializer


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
