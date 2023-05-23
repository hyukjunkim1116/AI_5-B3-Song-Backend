from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

class UserRegistrationAPIViewTestCase(APITestCase):
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