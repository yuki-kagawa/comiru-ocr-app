from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager, PermissionsMixin
from django.db import models
from django.conf import settings

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        """通常ユーザーの作成"""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)  # メールアドレスの正規化
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)  # パスワードをハッシュ化
        user.save(using=self._db)  # データベースに保存
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        """スーパーユーザーの作成"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()  # CustomUserManager を指定

    USERNAME_FIELD = 'email'  # `email` を認証フィールドとして使用
    REQUIRED_FIELDS = ['username']  # `username` を必須フィールドに設定

    def __str__(self):
        return self.username


class Child(models.Model):
    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='children'
    )
    name = models.CharField(max_length=100)
    birthday = models.DateField()
    gender_choices = [('M', '男の子'), ('F', '女の子')]
    gender = models.CharField(max_length=1, choices=gender_choices, null=True, blank=True)
    juku = models.CharField("ご利用中の塾", max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}（{self.parent.username}）"

