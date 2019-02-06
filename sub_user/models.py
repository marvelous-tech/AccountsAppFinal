from django.db import models
from base_user.models import BaseUserModel
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your models here.


class SubUserModel(models.Model):
    USER_TYPE_CHOICES = (
        ('accounts', 'Accounts'),
        ('co_admin', 'Co-Admin')
    )
    root_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='root_sub_user')
    base_user = models.ForeignKey(BaseUserModel, on_delete=models.CASCADE, related_name='sub_users')

    user_type = models.CharField(choices=USER_TYPE_CHOICES, default=USER_TYPE_CHOICES[0][0], max_length=45)
    uuid = models.UUIDField(unique=True)
    joined = models.DateField(blank=True)

    canAdd = models.BooleanField(default=True)
    canRetrieve = models.BooleanField(default=False)
    canEdit = models.BooleanField(default=False)
    canList = models.BooleanField(default=True)
    is_active = models.BooleanField(default=False)

    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.root_user.username
