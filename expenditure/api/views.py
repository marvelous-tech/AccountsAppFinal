from rest_framework import generics, status, filters
from expenditure.api.serializers import (
    ExpenditureHeadingModelSerializer,
    ExpenditureRecordModelSerializer,
    ExpenditureRecordHistoryModelSerializer,
    ExpenditureHeadingsHistoryModelSerializer,
    ExpenditureRecordForGivinLoanModelSafeSerializer,
    ExpenditureRecordModelForCreateSerializer,
    ExpenditureRecordForCreateForGivinLoanModelSafeSerializer
)
from project import permissions
from base_user.models import BaseUserModel
from sub_user.models import SubUserModel
from company.models import CompanyInfoModel
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from expenditure.api.filters import ExpenditureRecordFilter
from django.shortcuts import HttpResponse
import datetime
from utils import utils
import uuid
import os
from django.db.models import Q
today = datetime.datetime.today().strftime('%Y-%m-%d')


class ExpenditureHeadingListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ExpenditureHeadingModelSerializer
    permission_classes = [permissions.OnlyBaseUser, ]
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('heading_name', 'uuid', 'added', 'updated')
    ordering = ('-added', )

    def get_queryset(self):
        return self.request.user.base_user.expenditure_headings.filter(is_deleted=False)


class ExpenditureHeadingListAPIView(generics.ListAPIView):
    serializer_class = ExpenditureHeadingModelSerializer
    permission_classes = [permissions.BaseUserOrSubUser, ]
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('heading_name', 'uuid', 'added', 'updated')
    ordering = ('-added', )

    def get_queryset(self):
        queryset = None
        if BaseUserModel.objects.filter(base_user=self.request.user).exists():
            queryset = self.request.user.base_user.expenditure_headings.filter(is_deleted=False)
        elif SubUserModel.objects.filter(root_user=self.request.user).exists():
            queryset = self.request.user.root_sub_user.base_user.expenditure_headings.filter(is_deleted=False)
        return queryset


class ExpenditureHeadingRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ExpenditureHeadingModelSerializer
    permission_classes = [permissions.OnlyBaseUser, ]
    lookup_field = 'uuid'

    def get_queryset(self):
        return self.request.user.base_user.expenditure_headings.filter(is_deleted=False)


class ExpenditureHeadingHistory(generics.ListAPIView):
    serializer_class = ExpenditureHeadingsHistoryModelSerializer
    permission_classes = [permissions.OnlyBaseUser, ]

    def get_queryset(self):
        return self.request.user.base_user.expenditure_headings_history.all()


class ExpenditureRecordHistory(generics.ListAPIView):
    serializer_class = ExpenditureRecordHistoryModelSerializer
    permission_classes = [permissions.BaseUserOrSubUser, ]
    filter_backends = (filters.OrderingFilter, filters.SearchFilter)
    search_fields = (
        'action_by__username',
        'description',
        'old_uuid',
        'related_records__expend_heading__heading_name',
        'old_description',
        'new_description',
        'old_amount',
        'new_amount'
    )
    ordering_fields = ()
    ordering = ('-id',)

    def get_queryset(self):
        return utils.get_base_user(self.request).all_expenditure_records_history.all()


class ExpenditureRecordCreateAPIView(generics.CreateAPIView):
    serializer_class = ExpenditureRecordModelForCreateSerializer
    permission_classes = [
        permissions.FundIsNotLocked,
        permissions.BaseUserOrSubUser,
        permissions.SubUserCanAdd
    ]
    filter_backends = (filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = ExpenditureRecordFilter
    search_fields = (
        'expend_heading__heading_name',
        'description',
        'uuid',
        'added',
        'updated',
        'expend_by',
        'expend_date'
    )
    ordering_fields = ('added', 'expend_date', 'amount', 'expend_heading__heading_name')
    ordering = ('-id',)

    def get_queryset(self):
        queryset = utils.get_expend_model(
            filters={
                'is_for_refund': False,
                'is_for_return': False
            },
            only=(),
            request=self.request
        )
        return queryset
    
    def get_base_user(self):
        return utils.get_base_user(self.request)


class ExpenditureRecordListAPIView(generics.ListAPIView):
    serializer_class = ExpenditureRecordModelSerializer
    permission_classes = [
        permissions.BaseUserOrSubUser,
        permissions.SubUserCanList
    ]
    filter_backends = (filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = ExpenditureRecordFilter
    search_fields = (
        'expend_heading__heading_name',
        'description',
        'uuid',
        'added',
        'updated',
        'expend_by',
        'expend_date'
    )
    ordering_fields = ('added', 'expend_date', 'amount', 'expend_heading__heading_name')
    ordering = ('-id',)

    def get_queryset(self):
        queryset = utils.get_expend_model(
            filters={
                'added__year': datetime.datetime.today().year
            },
            only=(),
            request=self.request
        )
        return queryset


class ALLExpenditureRecordListAPIView(generics.ListAPIView):
    serializer_class = ExpenditureRecordModelSerializer
    permission_classes = [
        permissions.BaseUserOrSubUser,
        permissions.SubUserCanList
    ]
    filter_backends = (filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = ExpenditureRecordFilter
    search_fields = (
        'expend_heading__heading_name',
        'description',
        'uuid',
        'added',
        'updated',
        'expend_by',
        'expend_date'
    )
    ordering_fields = ('added', 'expend_date', 'amount', 'expend_heading__heading_name')
    ordering = ('-id',)

    def get_queryset(self):
        queryset = utils.get_expend_model(
            filters={},
            only=(),
            request=self.request
        )
        return queryset


class ExpenditureRecordRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = ExpenditureRecordModelSerializer
    permission_classes = [
        permissions.BaseUserOrSubUser,
        permissions.SubUserCanRetrieve
    ]
    lookup_field = 'uuid'

    def get_queryset(self):
        queryset = utils.get_expend_model(
            filters={
                'is_for_refund': False,
                'is_for_return': False
            },
            only=(),
            request=self.request
        )
        return queryset


class ExpenditureRecordRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ExpenditureRecordModelSerializer
    permission_classes = [
        permissions.FundIsNotLocked,
        permissions.BaseUserOrSubUser,
        permissions.SubUserFullAccess
    ]
    lookup_field = 'uuid'

    def get_queryset(self):
        queryset = utils.get_expend_model(
            filters={
                'is_for_refund': False,
                'is_for_return': False
            },
            only=(),
            request=self.request
        )
        return queryset


class ExpenditureRecordVerifyAPIView(generics.UpdateAPIView):
    permission_classes = [permissions.OnlyBaseUser, ]
    serializer_class = ExpenditureRecordModelSerializer
    lookup_field = 'uuid'

    def get_queryset(self):
        return self.request.user.base_user.all_expenditure_records.filter(is_verified=False, is_verified_once=False)


# Loan Giving


class ExpenditureRecordForGivingLoanCreateAPIView(ExpenditureRecordCreateAPIView):

    serializer_class = ExpenditureRecordForCreateForGivinLoanModelSafeSerializer
    
    def get_queryset(self):
        queryset = utils.get_expend_model(
            filters={
                'is_for_refund': False,
                'is_for_return': True
            },
            only=(),
            request=self.request
        )
        return queryset


class ExpenditureRecordForGivingLoanListAPIView(ExpenditureRecordListAPIView):

    serializer_class = ExpenditureRecordForGivinLoanModelSafeSerializer

    def get_queryset(self):
        queryset = utils.get_expend_model(
            filters={
                'is_for_refund': False,
                'is_for_return': True,
                'added__year': datetime.date.today().year
            },
            only=(),
            request=self.request
        )
        return queryset


class ExpenditureRecordForGivingLoanRetrieveAPIView(ExpenditureRecordRetrieveAPIView):

    serializer_class = ExpenditureRecordForGivinLoanModelSafeSerializer

    def get_queryset(self):
        queryset = utils.get_expend_model(
            filters={
                'is_for_refund': False,
                'is_for_return': False
            },
            only=(),
            request=self.request
        )
        return queryset


class ExpenditureRecordForGivingLoanRetrieveUpdateAPIView(ExpenditureRecordRetrieveUpdateAPIView):

    serializer_class = ExpenditureRecordForGivinLoanModelSafeSerializer

    def get_queryset(self):
        queryset = utils.get_expend_model(
            filters={
                'is_for_refund': False,
                'is_for_return': False
            },
            only=(),
            request=self.request
        )
        return queryset


# Loan Giving ---< END >---


class ExpenditureCheckoutToday(ExpenditureRecordCreateAPIView):
    permission_classes = [
        permissions.BaseUserOrSubUser
    ]
    headings = ['Head', 'Added by', 'Expended by', 'Amount (in Taka)', 'Expend time', 'Record added']
    attributes = ['expend_heading', 'added_by', 'expend_by', 'amount', 'expend_date', 'added']
    mimetype = 'text/csv'
    from_email = os.environ['EMAIL']

    def get_base_user(self):
        if BaseUserModel.objects.filter(base_user=self.request.user).exists():
            return self.request.user.base_user
        elif SubUserModel.objects.filter(root_user=self.request.user).exists():
            return self.request.user.root_sub_user.base_user

    def get_credit_funds(self):
        return self.get_base_user().credit_funds.filter(is_deleted=False)
    
    def get_expend_records(self):
        return self.get_base_user().all_expenditure_records.filter(is_deleted=False)
    
    def get_total_credit_amount(self):  # OK

        # Todo: Check if this algorithm has a mathmetical error in total credit amount

        expend_obj_ref_or_ret = self.get_expend_records().filter(
            Q(is_verified=True),
            Q(is_for_refund=True) | Q(is_for_return=True)
            )

        credit_obj = self.get_credit_funds()
        all_expend_amounts = [obj.amount for obj in expend_obj_ref_or_ret]
        all_credit_amounts = [obj.amount for obj in credit_obj]

        this_year_total_expend_amount = utils.sum_int_of_array(all_expend_amounts)
        this_year_total_credit_amount = utils.sum_int_of_array(all_credit_amounts)

        today_total_credit_fund_amount = this_year_total_credit_amount - this_year_total_expend_amount
        print(today_total_credit_fund_amount)

        return today_total_credit_fund_amount
    
    def get_total_expend_amount(self):
        expend_obj_non_ref_and_non_ret = self.get_expend_records().filter(
            Q(is_verified=True),
            Q(is_for_refund=False),
            Q(is_for_return=False)
            )
        all_expend_amounts = [obj.amount for obj in expend_obj_non_ref_and_non_ret]

        today_total_expend_amount = utils.sum_int_of_array(all_expend_amounts)

        return today_total_expend_amount
    
    def get_remaining_credit_fund_amount(self):

        expend_obj = self.get_expend_records().filter(Q(is_verified=True))
        credit_obj = self.get_credit_funds().filter()

        all_expend_obj_amounts = [obj.amount for obj in expend_obj]
        all_credit_obj_amounts = [obj.amount for obj in credit_obj]

        total_expend_amount = utils.sum_int_of_array(all_expend_obj_amounts)
        total_credit_amount = utils.sum_int_of_array(all_credit_obj_amounts)

        remaining_credit_fund_amount = total_credit_amount - total_expend_amount

        return remaining_credit_fund_amount
    
    def get_last_remaining_credit_fund_amount(self):

        expend_obj = self.get_expend_records().filter(
            Q(is_verified=True),
            Q(added__date__lt=datetime.date.today())
            )
        credit_obj = self.get_credit_funds().filter(
            Q(added__date__lt=datetime.date.today())
        )

        all_expend_obj_amounts = [obj.amount for obj in expend_obj]
        all_credit_obj_amounts = [obj.amount for obj in credit_obj]

        total_expend_amount = utils.sum_int_of_array(all_expend_obj_amounts)
        total_credit_amount = utils.sum_int_of_array(all_credit_obj_amounts)

        last_remaining_credit_fund_amount = total_credit_amount - total_expend_amount

        return last_remaining_credit_fund_amount

    def get_todays_open_credit_fund(self):
        expend_obj_ref_or_ret = self.get_expend_records().filter(
            Q(is_verified=True),
            Q(added__date__lt=datetime.date.today()),
            Q(is_for_refund=True) | Q(is_for_return=True)
            )

        credit_obj = self.get_credit_funds().filter(
            Q(added__date__lt=datetime.date.today())
            )

        all_expend_amounts = [obj.amount for obj in expend_obj_ref_or_ret]
        all_credit_amounts = [obj.amount for obj in credit_obj]

        total_expend_amount = utils.sum_int_of_array(all_expend_amounts)
        total_credit_amount = utils.sum_int_of_array(all_credit_amounts)

        todays_open_credit_fund = total_credit_amount - total_expend_amount

        return todays_open_credit_fund
    
    def get_todays_open_debit_amount(self):
        expend_obj_non_ref_and_non_ret = self.get_expend_records().filter(
            Q(is_verified=True),
            Q(added__date__lt=datetime.date.today()),
            Q(is_for_refund=False),
            Q(is_for_return=False)
            )
        all_expend_amounts = [obj.amount for obj in expend_obj_non_ref_and_non_ret]

        todays_open_debit_amount = utils.sum_int_of_array(all_expend_amounts)

        return todays_open_debit_amount
    
    def get_today_credit_fund(self):
        expend_obj_ref_or_ret = self.get_expend_records().filter(
            Q(is_verified=True),
            Q(added__date=datetime.date.today()),
            Q(is_for_refund=True) | Q(is_for_return=True)
            )

        credit_obj = self.get_credit_funds().filter(
            Q(added__date=datetime.date.today())
            )

        all_expend_amounts = [obj.amount for obj in expend_obj_ref_or_ret]
        all_credit_amounts = [obj.amount for obj in credit_obj]

        total_expend_amount = utils.sum_int_of_array(all_expend_amounts)
        total_credit_amount = utils.sum_int_of_array(all_credit_amounts)

        today_credit_fund = total_credit_amount - total_expend_amount

        return today_credit_fund
    
    def get_today_debit_amount(self):
        expend_obj_non_ref_and_non_ret = self.get_expend_records().filter(
            Q(is_verified=True),
            Q(added__date=datetime.date.today()),
            Q(is_for_refund=False),
            Q(is_for_return=False)
            )
        all_expend_amounts = [obj.amount for obj in expend_obj_non_ref_and_non_ret]

        todays_open_debit_amount = utils.sum_int_of_array(all_expend_amounts)

        return todays_open_debit_amount

    def get(self, request, *args, **kwargs):
        file_name = f'expenditure_records_of_{today}.pdf'
        subject = f'Accounts Application: Today - {today} - Checkout'
        body = f'''
        This is an automated e-mail from your application.
        Your daily expenditure records in {datetime.datetime.today().strftime("%d %B, %Y")}
        '''
        base_user = self.get_base_user()
        
        company = CompanyInfoModel.objects.get(base_user=base_user)

        context = {
            'company': company,
            'pdf_name': f'Expenditure {today}',
            'date': datetime.datetime.now(),
            'page_unique_id': uuid.uuid4(),
            'credit_items': self.get_credit_funds().filter(Q(added__date=datetime.date.today())),
            'debit_items': self.get_expend_records().filter(
                Q(added__date=datetime.date.today())
                ),
            'total_credit_amount': self.get_total_credit_amount(),
            'total_debit_amount': self.get_total_expend_amount(),
            'total_remaining_balance': self.get_remaining_credit_fund_amount(),
            'last_credit_amount': self.get_todays_open_credit_fund(),
            'last_debit_amount': self.get_todays_open_debit_amount(),
            'today_credit_amount': self.get_today_credit_fund(),
            'today_debit_amount': self.get_today_debit_amount(),
            'last_balance_amount': self.get_last_remaining_credit_fund_amount()
        }

        pdf = utils.django_render_to_pdf('expenditure_pdf_template.html', context)

        emails = base_user.all_emails.filter(is_active=True)
        to = [base_user.base_user.email, ]

        for email in emails:
            to.append(email.email_address)

        content = pdf.getvalue()
        utils.django_send_email_with_attachments(subject, body, self.from_email, to, file_name, content, 'text/pdf')

        return pdf

    def post(self, request, *args, **kwargs):
        return Response(data={'detail': 'Not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED, exception=True)


class ExpenditureRecordEmailCSV(ExpenditureCheckoutToday):

    def get(self, request, *args, **kwargs):
        items = self.filter_queryset(queryset=self.get_queryset())
        file_name = f'{today}_expenditure_record.csv'
        response = utils.django_download_generated_csv_from_model_object(
            file_name=file_name, query_set=items,
            headings=self.headings, attributes=self.attributes
        )
        subject = f'Accounts Application: All expenditure records (Generated {today}).'
        body = 'This is an automated e-mail from your application. Your files are given below.'
        base_user = self.get_base_user()

        emails = base_user.all_emails.filter(is_active=True)
        to = [base_user.base_user.email, ]

        for email in emails:
            to.append(email.email_address)

        content = response.getvalue()
        utils.django_send_email_with_attachments(subject, body, self.from_email, to, file_name, content, self.mimetype)

        return response


class ExpenditureRenderPDF(ExpenditureCheckoutToday):

    def get(self, request, *args, **kwargs):

        base_user = self.get_base_user()
        company = CompanyInfoModel.objects.get(base_user=base_user)

        context = {
            'company': company,
            'pdf_name': f'Expenditure {today}',
            'date': datetime.datetime.now(),
            'page_unique_id': uuid.uuid4(),
            'credit_items': self.get_credit_funds().filter(Q(added__date=datetime.date.today())),
            'debit_items': self.get_expend_records().filter(
                Q(added__date=datetime.date.today())
                ),
            'total_credit_amount': self.get_total_credit_amount(),
            'total_debit_amount': self.get_total_expend_amount(),
            'total_remaining_balance': self.get_remaining_credit_fund_amount(),
            'last_credit_amount': self.get_todays_open_credit_fund(),
            'last_debit_amount': self.get_todays_open_debit_amount(),
            'today_credit_amount': self.get_today_credit_fund(),
            'today_debit_amount': self.get_today_debit_amount(),
            'last_balance_amount': self.get_last_remaining_credit_fund_amount(),
            'host': request.get_host()
        }

        pdf = utils.django_render_to_pdf('expenditure_pdf_template.html', context)
        return HttpResponse(pdf, content_type='application/pdf')
