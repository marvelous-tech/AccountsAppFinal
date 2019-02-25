from django.db.models import Q, Sum
from rest_framework import generics
from rest_framework.response import Response
from project import permissions as main_permissions
from utils import utils
import datetime
import time
from credit.models import CreditFundModel
from expenditure.models import ExpenditureRecordModel


class InsightCreditDebitYearListAPIView(generics.ListAPIView):

    permission_classes = [main_permissions.BaseUserOrSubUser, ]

    def get_credit_model(self):
        return CreditFundModel.objects.filter(
            is_deleted=False,
            fund_added__year=datetime.date.today().year,
            base_user=utils.get_base_user(self.request)
        ).only('amount')

    def get_expend_model(self):
        return ExpenditureRecordModel.objects.filter(
            is_deleted=False,
            is_verified=True,
            expend_date__year=datetime.date.today().year,
            base_user=utils.get_base_user(self.request)
        ).only('amount')

    def get_queryset(self):
        return 0

    def get(self, request, *args, **kwargs):
        start = time.time()
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
        base_user = utils.get_base_user(self.request)
        this_year = datetime.date.today().year
        credit = self.get_credit_model()
        debit = self.get_expend_model()
        data = [
            {
                'month': months[k-1],
                'credit': credit.aggregate(
                    sum=utils.on_date_filter_balance(
                        {'fund_added__year__lt': this_year},
                        {'expend_date__year__lt': this_year},
                        base_user=base_user) + Sum('amount', filter=Q(fund_added__month__lte=k)) - debit.aggregate(
                        sum=Sum('amount',
                                filter=Q(expend_date__month__lte=k) & (Q(is_for_return=True) | Q(is_for_refund=True)))
                    )['sum']
                )['sum'],
                'debit': debit.aggregate(
                    sum=Sum('amount',
                            filter=Q(expend_date__month__lte=k) & ~(Q(is_for_return=True) | Q(is_for_refund=True)))
                )['sum'],
                'balance': utils.on_date_filter_balance(
                    {'fund_added__year': this_year, 'fund_added__month__lte': k},
                    {'expend_date__year': this_year, 'expend_date__month__lte': k},
                    base_user=base_user
                ),
                'credit_individual': credit.aggregate(
                    sum=utils.on_date_filter_balance(
                        {'fund_added__year__lt': this_year},
                        {'expend_date__year__lt': this_year},
                        base_user=base_user) + Sum('amount', filter=Q(fund_added__month=k)) - debit.aggregate(
                        sum=Sum('amount',
                                filter=Q(expend_date__month=k) & (Q(is_for_return=True) | Q(is_for_refund=True)))
                    )['sum'] or 0
                )['sum'] or 0,
                'debit_individual': debit.aggregate(
                    sum=Sum('amount',
                            filter=Q(expend_date__month=k) & ~(Q(is_for_return=True) | Q(is_for_refund=True)))
                )['sum'] or 0
            } for k in range(1, len(months)+1)
        ]
        end = time.time()
        print(f'{(end - start)*1000} ms')
        return Response(data=data)


class InsightCreditDebitMonthlyListAPIView(InsightCreditDebitYearListAPIView):

    def get(self, request, *args, **kwargs):
        start = time.time()
        base_user = utils.get_base_user(self.request)
        this_year = datetime.date.today().year
        month = int(self.request.query_params.get('month', datetime.date.today().month))
        days = utils.get_all_days_of_a_month(datetime.date.today().year, month)
        credit = self.get_credit_model()
        expenditure = self.get_expend_model()

        data = [
            {
                'day': k,
                'credit': credit.aggregate(
                    sum=utils.on_date_filter_balance(
                        {'fund_added__year__lt': this_year},
                        {'expend_date__year__lt': this_year},
                        base_user=base_user) + Sum('amount', filter=Q(fund_added__lte=datetime.date(this_year, month, k))) - expenditure.aggregate(
                        sum=Sum('amount',
                                filter=Q(expend_date__lte=datetime.date(this_year, month, k)) & (Q(is_for_return=True) | Q(is_for_refund=True)))
                    )['sum']
                )['sum'] or 0,
                'debit': expenditure.aggregate(
                    sum=Sum('amount',
                            filter=Q(expend_date__lte=datetime.date(this_year, month, k)) & ~(Q(is_for_return=True) | Q(is_for_refund=True)))
                )['sum'] or 0,
                'balance': utils.on_date_filter_balance(
                    {'fund_added__lte': datetime.date(this_year, month, k)},
                    {'expend_date__lte': datetime.date(this_year, month, k)},
                    base_user=base_user
                ),
                'credit_individual': credit.aggregate(
                    sum=Sum('amount', filter=Q(fund_added=datetime.date(this_year, month, k))) - expenditure.aggregate(
                        sum=Sum('amount',
                                filter=Q(expend_date=datetime.date(this_year, month, k)) & (Q(is_for_return=True) | Q(is_for_refund=True)))
                    )['sum']
                )['sum'] or 0,
                'debit_individual': expenditure.aggregate(
                    sum=Sum('amount',
                            filter=Q(expend_date=datetime.date(this_year, month, k)) & ~(Q(is_for_return=True) | Q(is_for_refund=True)))
                )['sum'] or 0
            } for k in range(1, len(days) + 1)
        ]
        end = time.time()
        print(f'{(end - start)*1000} ms')
        return Response(data=data)
