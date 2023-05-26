import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Photo
from .serializers import PhotoSerializer


class PhotoDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Photo.objects.get(pk=pk)
        except Photo.DoesNotExist:
            raise NotFound

    def put(self, request, pk):
        photo = self.get_object(pk)
        if photo.article and photo.article.owner != request.user:
            raise PermissionDenied
        serializer = PhotoSerializer(
            photo,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            updated_photo = serializer.save()
            return Response(
                PhotoSerializer(updated_photo).data,
            )
        else:
            return Response(
                serializer.errors,
                status=HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, pk):
        """사진 삭제하기"""
        photo = self.get_object(pk)
        if photo.article and photo.article.owner != request.user:
            raise PermissionDenied
        photo.delete()
        return Response(status=HTTP_200_OK)


class GetUploadURL(APIView):
    def post(self, request):
        """업로드용 URL 가져오기"""
        url = f"https://api.cloudflare.com/client/v4/accounts/{settings.CF_ID}/images/v2/direct_upload"
        one_time_url = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {settings.CF_TOKEN}",
            },
        )
        one_time_url = one_time_url.json()
        result = one_time_url.get("result")
        return Response(result)

    # {"id": result.get("id"), "uploadURL": result.get("uploadURL")}
