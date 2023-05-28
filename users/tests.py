from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from users.models import User

class UserRegistrationTest(APITestCase):
    """회원가입 테스트"""
    def test_registration_201(self):
        """return 201 Created"""
        url = reverse("user_view")        
        user_data = {
            "email":"test@test.test",
            "password":"1234",
            "nickname":"test",
            "age":"10",
            "gender":"F"
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 201)
        
    def test_registration_400(self):
        """return 400 Bad Request
        
        400 나오는 경우 :        
        email 형식으로 쓰지 않았을 때, age 외에 다른 필드 중 하나라도 작성하지 않았을 때
        """
        url = reverse("user_view")        
        user_data = {
            "email":"test",
            "password":"1234",
            "nickname":"test",
            "age":"10", # null = True
            "gender":"F"
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 400)
        
        
class UserTest(APITestCase):
    """유저 전체보기 테스트"""
    def test_user_all_view(self):
        url = reverse("user_all_view")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        
class UserProfileTest(APITestCase):
    def setUp(self):
        """유저 미리 만들기"""
        self.data = {"email": "test@test.test", "nickname":"test", "password": "1234"}
        self.user = User.objects.create_user("test@test.test", "test", "1234")
        
    def test_get_user_data(self):
        """유저 프로필 조회 테스트"""
        url = self.user.get_absolute_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], self.data["email"])