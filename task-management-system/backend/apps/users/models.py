from django.contrib.auth.models import AbstractUser
from django.db import models
class User(AbstractUser):
 """Custom User model"""
 email = models.EmailField(unique=True)
 bio = models.TextField(blank=True)
 avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

 def __str__(self):
 return self.username

 class Meta:
 db_table = 'users'
 verbose_name = 'User'
 verbose_name_plural = 'U