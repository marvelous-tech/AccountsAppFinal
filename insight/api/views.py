from django.db.models import Q
from rest_framework import generics
from rest_framework.response import Response
from project import permissions as main_permissions
from utils import utils
import datetime


class InsightCreditDebitModel:

    def __init__(self, month, credit, debit):
        self.month = month
        self.credit = credit
        self.debit = debit


class InsightCreditDebitYearListAPIView(generics.ListAPIView):

    permission_classes = [main_permissions.BaseUserOrSubUser, ]

    def get_queryset(self):
        return utils.get_base_user(self.request).credit_funds.all()

    def get(self, request, *args, **kwargs):
        months = [
            'January',
            'February',
            'March',
            'April',
            'May',
            'June',
            'July',
            'August',
            'September',
            'October',
            'November',
            'December'
        ]
        credit = utils.get_base_user(request).credit_funds.filter(
            is_deleted=False, fund_added__year=datetime.date.today().year).only('amount')
        expenditure = utils.get_base_user(request).all_expenditure_records.filter(
            is_deleted=False,
            expend_date__year=datetime.date.today().year).only('amount')
        data = [InsightCreditDebitModel(
            months[n],
            utils.sum_int_of_array(
                [obj.amount for obj in credit.filter(fund_added__month=(n+1))]
            ) - utils.sum_int_of_array(
                [obj.amount for obj in expenditure.filter(
                    Q(is_for_return=True) | Q(is_for_refund=True),
                    expend_date__month=(n+1)
                )]
            ),
            utils.sum_int_of_array(
                [obj.amount for obj in expenditure.filter(
                    expend_date__month=(n+1),
                    is_for_return=False,
                    is_for_refund=False
                )]
            )
            ) for n in range(len(months))]
        return Response(data=[
            {'month': obj.month, 'credit': obj.credit, 'debit': obj.debit} for obj in data
        ])
