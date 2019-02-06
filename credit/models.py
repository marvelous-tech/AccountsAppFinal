from django.db import models
from base_user.models import BaseUserModel
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.


class CreditFundSourceModel(models.Model):
    base_user = models.ForeignKey(BaseUserModel, on_delete=models.CASCADE, related_name='credit_fund_sources')
    source_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    uuid = models.UUIDField(unique=True)

    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.source_name


class CreditFundModel(models.Model):
    base_user = models.ForeignKey(BaseUserModel, on_delete=models.CASCADE, related_name='credit_funds')
    source = models.ForeignKey(CreditFundSourceModel, on_delete=models.CASCADE, related_name='funds')
    description = models.TextField(blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    amount = models.PositiveIntegerField()
    uuid = models.UUIDField(unique=True)
    fund_added = models.DateField()

    is_deleted = models.BooleanField(default=False)
    is_refundable = models.BooleanField(default=False)

    def __str__(self):
        return self.source.source_name


class CreditFundSettingsModel(models.Model):
    base_user = models.OneToOneField(BaseUserModel, on_delete=models.CASCADE, related_name='fund_settings')
    is_not_locked = models.BooleanField(default=False)

    def __str__(self):
        return self.base_user.base_user.username


class CreditFundSourceHistoryModel(models.Model):
    action_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="all_credit_fund_source_histories")

    base_user = models.ForeignKey(BaseUserModel, on_delete=models.DO_NOTHING,
                                  related_name="all_credit_fund_source_histories")
    credit_fund_source = models.ForeignKey(CreditFundSourceModel, on_delete=models.CASCADE,
                                           related_name="all_histories")

    is_deleted = models.BooleanField(default=False)
    is_updated = models.BooleanField(default=False)
    is_restored = models.BooleanField(default=False)

    old_source_name = models.CharField(max_length=120)
    new_source_name = models.CharField(max_length=120)

    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    description = models.TextField()

    old_uuid = models.UUIDField(unique=False)

    def __str__(self):
        return self.credit_fund_source.source_name


class CreditFundHistoryModel(models.Model):
    action_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="all_credit_fund_histories")

    base_user = models.ForeignKey(BaseUserModel, on_delete=models.DO_NOTHING, related_name="all_credit_fund_histories")
    credit_fund = models.ForeignKey(CreditFundModel, on_delete=models.DO_NOTHING, related_name="all_histories")

    is_deleted = models.BooleanField(default=False)
    is_updated = models.BooleanField(default=False)
    is_restored = models.BooleanField(default=False)

    # ------------------
    old_source = models.ForeignKey(CreditFundSourceModel, on_delete=models.DO_NOTHING, related_name="all_old_histories")
    new_source = models.ForeignKey(CreditFundSourceModel, on_delete=models.DO_NOTHING, related_name="all_new_histories")
    # --------------------
    old_description = models.TextField(blank=True, null=True)
    new_description = models.TextField(blank=True, null=True)
    # -----------------
    old_fund_added = models.DateField()
    new_fund_added = models.DateField()
    # -----------------
    old_amount = models.PositiveIntegerField()
    new_amount = models.PositiveIntegerField()
    # -------------------

    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    description = models.TextField()

    old_uuid = models.UUIDField(unique=False)

    def __str__(self):
        return self.action_by.username

    def get_credit_fund(self):
        return self.credit_fund.__str__()

    def get_old_source(self):
        return self.old_source.__str__()

    def get_new_source(self):
        return self.new_source.__str__()

    def get_is_refundable(self):
        return self.credit_fund.is_refundable




