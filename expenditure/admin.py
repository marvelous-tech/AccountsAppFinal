from django.contrib import admin
from expenditure.models import (
    ExpenditureHeadingModel,
    ExpenditureHeadingHistoryModel,
    ExpenditureRecordHistoryModel,
    ExpenditureRecordModel
)
# Register your models here.

admin.site.register(ExpenditureHeadingModel)
admin.site.register(ExpenditureRecordModel)
admin.site.register(ExpenditureHeadingHistoryModel)
admin.site.register(ExpenditureRecordHistoryModel)
