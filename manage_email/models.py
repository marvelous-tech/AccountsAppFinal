from django.db import models
from base_user.models import BaseUserModel

# Create your models here.


class ManageEmailModel(models.Model):
    base_user = models.ForeignKey(BaseUserModel, on_delete=models.CASCADE, related_name="all_emails")
    email_address = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.base_user.base_user.username
