from django.db.models import Q
from rest_framework import generics
from rest_framework.response import Response
from project import permissions as main_permissions
from utils import utils
import datetime


class InsightCreditDebitYearlyModel:

    def __init__(self, month, credit, debit, credit_individual, debit_individual):
        self.month = month
        self.credit = credit
        self.debit = debit
        self.credit_individual = credit_individual
        self.debit_individual = debit_individual


class InsightCreditDebitMonthlyModel:

    def __init__(self, day, credit, debit, credit_individual, debit_individual):
        self.day = day
        self.credit = credit
        self.debit = debit
        self.credit_individual = credit_individual
        self.debit_individual = debit_individual


class InsightCreditDebitYearListAPIView(generics.ListAPIView):

    permission_classes = [main_permissions.BaseUserOrSubUser, ]

    def get_main_credit(self):
        return utils.get_base_user(self.request).credit_funds.filter(
            is_deleted=False
        ).only('amount')

    def get_main_expend(self):
        return utils.get_base_user(self.request).all_expenditure_records.filter(
            is_deleted=False,
            is_verified=True
        ).only('amount')

    def get_credit_model(self):
        return utils.get_base_user(self.request).credit_funds.filter(
            is_deleted=False, fund_added__year=datetime.date.today().year).only('amount')

    def get_expend_model(self):
        return utils.get_base_user(self.request).all_expenditure_records.filter(
            is_deleted=False,
            expend_date__year=datetime.date.today().year,
            is_verified=True).only('amount')

    def get_balance_last_all_years(self):
        last_years_credit = utils.sum_int_of_array([obj.amount for obj in self.get_main_credit().filter(
            fund_added__year__lt=datetime.date.today().year)])
        last_years_expend = utils.sum_int_of_array([obj.amount for obj in self.get_main_expend().filter(
            expend_date__year__lt=datetime.date.today().year)])
        return last_years_credit - last_years_expend

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
        credit = self.get_credit_model()
        expenditure = self.get_expend_model()
        data = [InsightCreditDebitYearlyModel(
            months[n],
            self.get_balance_last_all_years() + utils.sum_int_of_array(
                [obj.amount for obj in credit.filter(fund_added__month__lte=(n+1))]
            ) - utils.sum_int_of_array(
                [obj.amount for obj in expenditure.filter(
                    Q(is_for_return=True) | Q(is_for_refund=True),
                    expend_date__month__lte=(n+1)
                )]
            ),
            utils.sum_int_of_array(
                [obj.amount for obj in expenditure.filter(
                    expend_date__month__lte=(n+1),
                    is_for_return=False,
                    is_for_refund=False
                )]
            ),
            utils.sum_int_of_array(
                [obj.amount for obj in credit.filter(fund_added__month=(n + 1))]
            ) - utils.sum_int_of_array(
                [obj.amount for obj in expenditure.filter(
                    Q(is_for_return=True) | Q(is_for_refund=True),
                    expend_date__month=(n + 1)
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
            {'month': obj.month, 'credit': obj.credit,
             'debit': obj.debit, 'credit_individual': obj.credit_individual,
             'debit_individual': obj.debit_individual} for obj in data
        ])


class InsightCreditDebitMonthlyListAPIView(InsightCreditDebitYearListAPIView):

    def get(self, request, *args, **kwargs):
        month = self.request.query_params.get('month', datetime.date.today().month)
        month = int(month)
        days = utils.get_all_days_of_a_month(datetime.date.today().year, month)
        credit = self.get_credit_model()
        expenditure = self.get_expend_model()
        data = [InsightCreditDebitMonthlyModel(
            days[n],
            self.get_balance_last_all_years() + utils.sum_int_of_array(
                [obj.amount for obj in credit.filter(
                    fund_added__lte=datetime.date(year=datetime.date.today().year, month=month, day=(n+1))
                )]
            ) - utils.sum_int_of_array(
                [obj.amount for obj in expenditure.filter(
                    Q(is_for_return=True) | Q(is_for_refund=True),
                    expend_date__lte=datetime.date(year=datetime.date.today().year, month=month, day=(n+1))
                )]
            ),
            utils.sum_int_of_array(
                [obj.amount for obj in expenditure.filter(
                    expend_date__lte=datetime.date(year=datetime.date.today().year, month=month, day=(n+1)),
                    is_for_return=False,
                    is_for_refund=False
                )]
            ),
            utils.sum_int_of_array(
                [obj.amount for obj in credit.filter(
                    fund_added=datetime.date(year=datetime.date.today().year, month=month, day=(n + 1))
                )]
            ) - utils.sum_int_of_array(
                [obj.amount for obj in expenditure.filter(
                    Q(is_for_return=True) | Q(is_for_refund=True),
                    expend_date=datetime.date(year=datetime.date.today().year, month=month, day=(n + 1))
                )]
            ),
            utils.sum_int_of_array(
                [obj.amount for obj in expenditure.filter(
                    expend_date=datetime.date(year=datetime.date.today().year, month=month, day=(n+1)),
                    is_for_return=False,
                    is_for_refund=False
                )]
            )
        ) for n in range(len(days))]
        return Response(data=[
            {'day': obj.day, 'credit': obj.credit,
             'debit': obj.debit, 'credit_individual': obj.credit_individual,
             'debit_individual': obj.debit_individual} for obj in data
        ])
