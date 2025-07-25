from django.db import models
from django.contrib.auth.models import User
import os
from django.utils.text import slugify

def avatar_upload_path(instance, filename):
    # Use username instead of email to avoid URL encoding issues
    username = slugify(instance.user.username)
    return f'avatars/{username}/{filename}'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    avatar = models.ImageField(upload_to=avatar_upload_path, blank=True, null=True)
    role = models.CharField(max_length=20, default='server')
    hire_date = models.DateField(blank=True, null=True)
    department = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
