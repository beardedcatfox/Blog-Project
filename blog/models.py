from django.contrib.auth.models import AbstractUser
from django.db import models

from storages.backends.s3boto3 import S3Boto3Storage


class PostImagesStorage(S3Boto3Storage):
    location = 'post_images'


class UserPhotoStorage(S3Boto3Storage):
    location = 'user_photo'


class Author(AbstractUser):
    profile_photo = models.ImageField(blank=True, verbose_name='Photo', storage=UserPhotoStorage(),
                                      upload_to='user_photo/')
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    bio = models.TextField(max_length=1200, verbose_name='Bio', blank=True)
    birth_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.username


class Post(models.Model):
    owner = models.ForeignKey(Author, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    short_description = models.CharField(max_length=255)
    full_description = models.TextField()
    image = models.ImageField(upload_to='post_images/', storage=PostImagesStorage(), blank=True)
    is_published = models.BooleanField(default=False)
    published_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.CharField(max_length=200)
    text = models.TextField()
    is_published = models.BooleanField(default=False)
    published_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author}"
