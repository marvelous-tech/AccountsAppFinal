from django.db import models
from credit.models import CreditFundModel
from expenditure.models import ExpenditureRecordModel
from base_user.models import BaseUserModel
# Create your models here.


class CreditFundOnLoanModel(models.Model):
    base_user = models.ForeignKey(BaseUserModel, on_delete=models.CASCADE, related_name="loan_funds")
    credit_fund = models.OneToOneField(CreditFundModel, on_delete=models.CASCADE, related_name="loan")

    def __str__(self):
        return self.credit_fund.source.source_name


class ExpenditureRecordOnLoanModel(models.Model):
    base_user = models.ForeignKey(BaseUserModel, on_delete=models.CASCADE, related_name="loan_refunds")
    expenditure_record_model = models.OneToOneField(ExpenditureRecordModel, on_delete=models.CASCADE,
                                                    related_name="loan")

    @property
    def amount(self):
        return self.expenditure_record_model.amount
