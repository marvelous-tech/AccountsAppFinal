from django.contrib import admin
from credit.models import (
    CreditFundModel,
    CreditFundSourceModel,
    CreditFundSettingsModel,
    CreditFundSourceHistoryModel,
    CreditFundHistoryModel
)

# Register your models here.

admin.site.register(CreditFundModel)
admin.site.register(CreditFundSourceModel)
admin.site.register(CreditFundSettingsModel)
admin.site.register(CreditFundSourceHistoryModel)
admin.site.register(CreditFundHistoryModel)
