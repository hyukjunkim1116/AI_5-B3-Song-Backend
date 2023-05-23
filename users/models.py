from django.db import models
from django.contrib.auth.models import AbstractBaseUser


# Create your models here.
class User(AbstractBaseUser):
    username = models.CharField("유저 아이디", max_length=20, unique=True)
    email = models.EmailField("이메일", max_length=255, unique=True)
    name = models.CharField("이름", max_length=20, blank=True, null=True)
    introduction = models.CharField("자기 소개", max_length=255, blank=True, null=True)

    followings = models.ManyToManyField(
        "self", symmetrical=False, related_name="followers", blank=True
    )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
