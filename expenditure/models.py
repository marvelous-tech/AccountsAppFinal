from django.db import models
from base_user.models import BaseUserModel
from django.contrib.auth import get_user_model
User = get_user_model()
# Create your models here.


class ExpenditureHeadingModel(models.Model):
    base_user = models.ForeignKey(BaseUserModel, on_delete=models.DO_NOTHING, related_name='expenditure_headings')
    heading_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    uuid = models.UUIDField(unique=True)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.heading_name


class ExpenditureHeadingHistoryModel(models.Model):
    action_by = models.ForeignKey(User, on_delete=models.DO_NOTHING,
                                  related_name='expenditure_headings_history')

    base_user = models.ForeignKey(BaseUserModel, on_delete=models.DO_NOTHING,
                                  related_name='expenditure_headings_history')

    related_heading = models.ForeignKey(ExpenditureHeadingModel, on_delete=models.DO_NOTHING,
                                        related_name="all_history")

    old_heading_name = models.CharField(max_length=122)
    new_heading_name = models.CharField(max_length=122)

    old_description = models.TextField(blank=True, null=True)
    new_description = models.TextField(blank=True, null=True)

    old_uuid = models.UUIDField(unique=False)

    is_updated = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_restored = models.BooleanField(default=False)

    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    description = models.TextField()

    def __str__(self):
        return self.related_heading.heading_name


class ExpenditureRecordModel(models.Model):
    added_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='expenditure_records')

    base_user = models.ForeignKey(BaseUserModel, on_delete=models.DO_NOTHING, related_name='all_expenditure_records')
    expend_heading = models.ForeignKey(ExpenditureHeadingModel, on_delete=models.DO_NOTHING, related_name='all_records')

    expend_by = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    amount = models.PositiveIntegerField()
    is_verified = models.BooleanField(default=False)
    expend_date = models.DateField()

    uuid = models.UUIDField(unique=True)

    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    is_deleted = models.BooleanField(default=False)
    is_for_refund = models.BooleanField(default=False)

    def __str__(self):
        return self.added_by.username


class ExpenditureRecordHistoryModel(models.Model):
    action_by = models.ForeignKey(User, on_delete=models.DO_NOTHING,
                                  related_name='expenditure_records_history')
    base_user = models.ForeignKey(BaseUserModel, on_delete=models.DO_NOTHING,
                                  related_name='all_expenditure_records_history')

    related_records = models.ForeignKey(ExpenditureRecordModel, on_delete=models.CASCADE, related_name="all_history")

    old_expend_heading = models.ForeignKey(ExpenditureHeadingModel,
                                           on_delete=models.DO_NOTHING, related_name='old_all_records_history')
    new_expend_heading = models.ForeignKey(ExpenditureHeadingModel,
                                           on_delete=models.DO_NOTHING, related_name='new_all_records_history')

    old_expend_by = models.CharField(max_length=100)
    new_expend_by = models.CharField(max_length=100)

    old_description = models.TextField(blank=True, null=True)
    new_description = models.TextField(blank=True, null=True)

    old_amount = models.PositiveIntegerField()
    new_amount = models.PositiveIntegerField()

    old_is_verified = models.BooleanField(default=False)
    new_is_verified = models.BooleanField(default=False)

    old_expend_date = models.DateField()
    new_expend_date = models.DateField()

    old_uuid = models.UUIDField(unique=False)

    is_updated = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_restored = models.BooleanField(default=False)

    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    description = models.TextField()

    def __str__(self):
        return self.action_by.username

    def get_related_records(self):
        return self.related_records.expend_heading.heading_name

    def get_old_expend_heading(self):
        return self.old_expend_heading.heading_name

    def get_new_expend_heading(self):
        return self.new_expend_heading.heading_name

    def get_is_for_refund(self):
        return self.related_records.is_for_refund
