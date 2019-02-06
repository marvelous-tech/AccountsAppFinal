from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your models here.


class UserExtraInfoModel(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_extra_info')

    is_approved = models.BooleanField(default=False)
    is_not_locked = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    base_user = models.BooleanField(default=False)
    sub_user = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
