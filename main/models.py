from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils import timezone
import os

def user_directory_path(instance, filename):
    return f'user_{instance.user.id}/{filename}'

class User(AbstractUser):
    is_ops_user = models.BooleanField(default=False)
    is_client_user = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',  
        blank=True,
        help_text='The groups this user belongs to.',
        related_query_name='user',
        verbose_name='groups'
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_set', 
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='user',
        verbose_name='user permissions'
    )

    def __str__(self):
        return self.username

class FileUpload(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to=user_directory_path)  
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.file.name}'
