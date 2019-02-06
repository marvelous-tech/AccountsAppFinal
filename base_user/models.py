from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
# Create your models here.


class BaseUserModel(models.Model):

    base_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='base_user')
    is_admin = models.BooleanField(default=True)

    uuid = models.UUIDField(unique=True)
    joined = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.base_user.username
