from django.db import models
from base_user.models import BaseUserModel

# Create your models here.


class CompanyInfoModel(models.Model):
    COMPANY_TYPE_CHOICES = (
        ('gr', 'Garment'),
        ('bh', 'Buying House'),
        ('as', 'Association'),
        ('en', 'Enterprise'),
        ('co', 'Corporation'),
        ('ps', 'Personal')
    )
    base_user = models.OneToOneField(BaseUserModel, on_delete=models.CASCADE, related_name='company_user')

    name = models.CharField(max_length=200)
    address = models.TextField()
    company_type = models.CharField(max_length=45, choices=COMPANY_TYPE_CHOICES, default=COMPANY_TYPE_CHOICES[0][0])
    created = models.DateField(blank=True, null=True)
    uuid = models.UUIDField(blank=True)

    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.name
