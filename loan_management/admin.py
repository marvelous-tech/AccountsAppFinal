from django.contrib import admin
from loan_management import models
# Register your models here.
admin.site.register(models.CreditFundOnLoanModel)
admin.site.register(models.ExpenditureRecordOnLoanModel)
