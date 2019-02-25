import django
import os
import datetime
import time
import pprint

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.db.models import Sum, F, Subquery, Q, ExpressionWrapper, IntegerField
from credit.models import CreditFundModel
from expenditure.models import ExpenditureRecordModel
from utils import utils

credit = CreditFundModel.objects.filter(
        is_deleted=False,
        fund_added__year=2019,
        base_user=1
    ).only('amount')
debit = ExpenditureRecordModel.objects.filter(
    is_deleted=False,
    is_verified=True,
    expend_date__year=2019,
    base_user=1
).only('amount')
expenditure = ExpenditureRecordModel.objects.filter(
    is_deleted=False,
    is_verified=True,
    expend_date__year=2019,
    base_user=1
).only('amount')


class InsightCreditDebitMonthlyModel:

    def __init__(self, day, credit, debit, balance, credit_individual, debit_individual):
        self.day = day
        self.credit = credit
        self.debit = debit
        self.balance = balance
        self.credit_individual = credit_individual
        self.debit_individual = debit_individual


def on_date_filter_balance(date_filters_credit={}, date_filters_expenditure={}, base_user=1):
    _credit = CreditFundModel.objects.filter(
        base_user=base_user,
        **date_filters_credit,
        is_deleted=False
    ).only('amount')
    _expenditure = ExpenditureRecordModel.objects.filter(
        base_user=base_user,
        **date_filters_expenditure,
        is_deleted=False,
        is_verified=True
    ).only('amount')
    sum_value = _credit.aggregate(
        sum=Sum('amount') - _expenditure.aggregate(sum=Sum('amount'))['sum'])['sum']
    return sum_value or 0


def year_month_lt_balance(year, month, base_user=1):
    return on_date_filter_balance(
        {'fund_added__year': year, 'fund_added__month__lte': month},
        {'expend_date__year': year, 'expend_date__month__lte': month},
        base_user=base_user
    )


def debug():
    '''
    data = [
        {
            'month': k,
            'credit': credit.aggregate(
                sum=on_date_filter_balance(
                    {'fund_added__year__lt': 2019},
                    {'expend_date__year__lt': 2019},
                    base_user=1) + Sum('amount', filter=Q(fund_added__month__lte=k)) - debit.aggregate(
                    sum=Sum('amount',
                            filter=Q(expend_date__month__lte=k) & (Q(is_for_return=True) | Q(is_for_refund=True)))
                )['sum']
            )['sum'] or 0,
            'debit': debit.aggregate(
                    sum=Sum('amount',
                            filter=Q(expend_date__month__lte=k) & ~(Q(is_for_return=True) | Q(is_for_refund=True)))
                )['sum'] or 0,
            'balance': on_date_filter_balance(
                {'fund_added__year': 2019, 'fund_added__month__lte': k},
                {'expend_date__year': 2019, 'expend_date__month__lte': k},
                base_user=1
            ),
            'credit_absolute': credit.aggregate(
                sum=on_date_filter_balance(
                    {'fund_added__year__lt': 2019},
                    {'expend_date__year__lt': 2019},
                    base_user=1) + Sum('amount', filter=Q(fund_added__month=k)) - debit.aggregate(
                    sum=Sum('amount',
                            filter=Q(expend_date__month=k) & (Q(is_for_return=True) | Q(is_for_refund=True)))
                )['sum']
            )['sum'] or 0,
            'debit_absolute': debit.aggregate(
                    sum=Sum('amount',
                            filter=Q(expend_date__month=k) & ~(Q(is_for_return=True) | Q(is_for_refund=True)))
                )['sum'] or 0
        } for k in range(1, 13)
    ]
    '''

    month = '2'
    month = int(month)
    days = utils.get_all_days_of_a_month(datetime.date.today().year, month)

    data2 = [
        {
            'day': k,
            'credit': credit.aggregate(
                sum=on_date_filter_balance(
                    {'fund_added__year__lt': 2019},
                    {'expend_date__year__lt': 2019},
                    base_user=1) + Sum('amount', filter=Q(fund_added__lte=datetime.date(2019, month, k))) - debit.aggregate(
                    sum=Sum('amount',
                            filter=Q(expend_date__lte=datetime.date(2019, month, k)) & (Q(is_for_return=True) | Q(is_for_refund=True)))
                )['sum']
            )['sum'] or 0,
            'debit': debit.aggregate(
                sum=Sum('amount',
                        filter=Q(expend_date__lte=datetime.date(2019, month, k)) & ~(Q(is_for_return=True) | Q(is_for_refund=True)))
            )['sum'] or 0,
            'balance': on_date_filter_balance(
                {'fund_added__lte': datetime.date(2019, month, k)},
                {'expend_date__lte': datetime.date(2019, month, k)},
                base_user=1
            ),
            'credit_individual': credit.aggregate(
                sum=Sum('amount', filter=Q(fund_added=datetime.date(2019, month, k))) - debit.aggregate(
                    sum=Sum('amount',
                            filter=Q(expend_date=datetime.date(2019, month, k)) & (Q(is_for_return=True) | Q(is_for_refund=True)))
                )['sum']
            )['sum'] or 0,
            'debit_individual': debit.aggregate(
                sum=Sum('amount',
                        filter=Q(expend_date=datetime.date(2019, month, k)) & ~(Q(is_for_return=True) | Q(is_for_refund=True)))
            )['sum'] or 0
        } for k in range(1, len(days) + 1)
    ]

    pprint.pprint(pprint.pformat(data2))


def debug2():
    month = '2'
    month = int(month)
    days = utils.get_all_days_of_a_month(datetime.date.today().year, month)
    data = [InsightCreditDebitMonthlyModel(
        days[n],
        on_date_filter_balance(
            {'fund_added__year__lt': 2019},
            {'expend_date__year__lt': 2019},
            base_user=1) + utils.sum_int_of_array(
            [obj.amount for obj in credit.filter(
                fund_added__lte=datetime.date(year=datetime.date.today().year, month=month, day=(n + 1))
            )]
        ) - utils.sum_int_of_array(
            [obj.amount for obj in expenditure.filter(
                Q(is_for_return=True) | Q(is_for_refund=True),
                expend_date__lte=datetime.date(year=datetime.date.today().year, month=month, day=(n + 1))
            )]
        ),
        utils.sum_int_of_array(
            [obj.amount for obj in expenditure.filter(
                expend_date__lte=datetime.date(year=datetime.date.today().year, month=month, day=(n + 1)),
                is_for_return=False,
                is_for_refund=False
            )]
        ),
        utils.sum_int_of_array(
            [obj.amount for obj in credit.filter(
                fund_added__lte=datetime.date(year=datetime.date.today().year, month=month, day=(n + 1))
            )]
        ) - utils.sum_int_of_array(
            [obj.amount for obj in expenditure.filter(
                expend_date__lte=datetime.date(year=datetime.date.today().year, month=month, day=(n + 1))
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
                expend_date=datetime.date(year=datetime.date.today().year, month=month, day=(n + 1)),
                is_for_return=False,
                is_for_refund=False
            )]
        )
    ) for n in range(len(days))]
    pprint.pprint(pprint.pformat([
        {'day': obj.day, 'credit': obj.credit,
         'debit': obj.debit, 'credit_individual': obj.credit_individual,
         'balance': obj.balance, 'debit_individual': obj.debit_individual} for obj in data
    ]))


def explain():
    ex = debit.annotate(
                    sum=Sum('amount',
                            filter=Q(expend_date__month__lte=12) & (~Q(is_for_return=True) | ~Q(is_for_refund=True)))
                ).query
    print(ex)


if __name__ == '__main__':
    start = time.time()
    debug2()
    # explain()
    end = time.time()
    print(f'{(end - start)*1000} ms')
