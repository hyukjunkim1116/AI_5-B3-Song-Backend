from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.urls import reverse


class UserManager(BaseUserManager):
    def create_user(self, email, nickname, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            nickname=nickname,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nickname, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """

        user = self.create_user(
            email,
            nickname=nickname,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    GENDERS = [
        ("M", "Male"),
        ("F", "Female"),
    ]
    avatar = models.URLField(blank=True)
    email = models.EmailField("이메일", max_length=255, unique=True)
    nickname = models.CharField("닉네임", max_length=20, unique=True)
    password = models.CharField("비밀번호", max_length=256)
    genre = models.CharField("장르", max_length=256, null=True, blank=True)
    age = models.IntegerField("나이", null=True)
    gender = models.CharField("성별", max_length=1, choices=GENDERS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    followings = models.ManyToManyField(
        "self", symmetrical=False, related_name="followers", blank=True
    )

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nickname"]

    def __str__(self):
        return self.nickname
    
    def get_absolute_url(self):
        return reverse("profile_view", kwargs={"user_id": self.pk})

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
