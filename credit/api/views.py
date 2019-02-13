from rest_framework import generics, status, filters
from credit.api import serializers
from project import permissions
from base_user.models import BaseUserModel
from sub_user.models import SubUserModel
from company.models import CompanyInfoModel
from rest_framework.response import Response
from credit.api.filters import CreditFundFilter
from django_filters.rest_framework import DjangoFilterBackend
from utils import utils
import os
import datetime
import uuid


class CreditFundSourceListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = serializers.CreditFundSourceModelSerializer
    permission_classes = [permissions.OnlyBaseUser, ]
    filter_backends = (filters.OrderingFilter, filters.SearchFilter)
    search_fields = ('description', 'uuid', 'source_name')
    ordering_fields = ('added', 'source_name', 'amount')
    ordering = ('-id',)

    def get_queryset(self):
        return self.request.user.base_user.credit_fund_sources.filter(is_deleted=False)


class CreditFundSourceListAPIView(generics.ListAPIView):
    serializer_class = serializers.CreditFundSourceModelSerializer
    permission_classes = [permissions.BaseUserOrSubUser, permissions.SubUserCanList]
    filter_backends = (filters.OrderingFilter, filters.SearchFilter)
    search_fields = ('description', 'uuid', 'source_name')
    ordering_fields = ('added', 'source_name', 'amount')
    ordering = ('-id',)

    def get_queryset(self):
        if BaseUserModel.objects.filter(base_user=self.request.user).exists():
            return self.request.user.base_user.credit_fund_sources.filter(is_deleted=False)
        elif SubUserModel.objects.filter(root_user=self.request.user).exists():
            return self.request.user.root_sub_user.base_user.credit_fund_sources.filter(is_deleted=False)


class CreditFundsAccordingToSourcesListAPIView(CreditFundSourceListCreateAPIView):
    serializer_class = serializers.CreditFundsAccordingToSourcesSerializer

    def post(self, request, *args, **kwargs):
        return Response(data={'detail': 'Not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED, exception=True)


class CreditFundSourceRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = serializers.CreditFundSourceModelSerializer
    permission_classes = [permissions.OnlyBaseUser, permissions.FundIsNotLocked]
    lookup_field = 'uuid'

    def get_queryset(self):
        return self.request.user.base_user.credit_fund_sources.filter(is_deleted=False)


class CreditFundListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = serializers.CreditFundModelForCreateSerializer
    permission_classes = [permissions.OnlyBaseUser, ]
    filter_backends = (filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend)
    search_fields = ('description', 'uuid')
    ordering_fields = ('added', 'source__source_name', 'amount')
    ordering = ('-id', )
    filterset_class = CreditFundFilter

    def get_queryset(self):
        return self.request.user.base_user.credit_funds.all().filter(
            added__year=datetime.datetime.today().year,
            is_deleted=False,
            is_returnable=False,
            is_refundable=False
            )


class ALLCreditFundListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = serializers.CreditFundModelSerializer
    permission_classes = [permissions.OnlyBaseUser, ]
    filter_backends = (filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend)
    search_fields = ('description', 'uuid')
    ordering_fields = ('added', 'source__source_name', 'amount')
    ordering = ('-id', )
    filterset_class = CreditFundFilter

    def get_queryset(self):
        return self.request.user.base_user.credit_funds.filter(
            is_deleted=False,
            is_returnable=False,
            is_refundable=False
            )


class CreditFundRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = serializers.CreditFundModelSerializer
    permission_classes = [permissions.OnlyBaseUser, permissions.FundIsNotLocked]
    lookup_field = 'uuid'

    def get_queryset(self):
        return self.request.user.base_user.credit_funds.filter(
            is_deleted=False,
            is_refundable=False,
            is_returnable=False
            )


class CreditFundRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = serializers.CreditFundModelSerializer
    permission_classes = [permissions.OnlyBaseUser, ]
    lookup_field = 'uuid'

    def get_queryset(self):
        return self.request.user.base_user.credit_funds.filter(
            is_deleted=False,
            is_refundable=False,
            is_returnable=False
            )


class CreditFundListAPIView(generics.ListAPIView):
    serializer_class = serializers.CreditFundModelSerializer
    permission_classes = [permissions.BaseUserOrSubUser, permissions.SubUserCanList]
    filter_backends = (filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend)
    search_fields = ('description', 'uuid')
    ordering_fields = ('added', 'source__source_name', 'amount')
    ordering = ('-id', )
    filterset_class = CreditFundFilter

    def get_queryset(self):
        if BaseUserModel.objects.filter(base_user=self.request.user).exists():
            return self.request.user.base_user.credit_funds.filter(
                added__year=datetime.datetime.today().year, 
                is_deleted=False,
                is_returnable=False,
                is_refundable=False
                )
        elif SubUserModel.objects.filter(root_user=self.request.user).exists():
            return self.request.user.root_sub_user.base_user.credit_funds.filter(
                added__year=datetime.datetime.today().year,
                is_deleted=False,
                is_returnable=False,
                is_refundable=False
                )


class ALLCreditFundListAPIView(generics.ListAPIView):
    serializer_class = serializers.CreditFundModelSerializer
    permission_classes = [permissions.BaseUserOrSubUser, permissions.SubUserCanList]
    filter_backends = (filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend)
    search_fields = ('description', 'uuid')
    ordering_fields = ('added', 'source__source_name', 'amount')
    ordering = ('-id', )
    filterset_class = CreditFundFilter

    def get_queryset(self):
        if BaseUserModel.objects.filter(base_user=self.request.user).exists():
            return self.request.user.base_user.credit_funds.filter(
                is_deleted=False
                )
        elif SubUserModel.objects.filter(root_user=self.request.user).exists():
            return self.request.user.root_sub_user.base_user.credit_funds.filter(
                is_deleted=False
                )


class CreditFundSettingsView(generics.RetrieveAPIView):
    serializer_class = serializers.CreditFundSettingsModelSerializer
    permission_classes = [permissions.BaseUserOrSubUser, ]

    def get_object(self):
        if BaseUserModel.objects.filter(base_user=self.request.user).exists():
            return self.request.user.base_user.fund_settings
        elif SubUserModel.objects.filter(root_user=self.request.user).exists():
            return self.request.user.root_sub_user.base_user.fund_settings


class CreditFundSettingsEditView(generics.RetrieveUpdateAPIView):
    serializer_class = serializers.CreditFundSettingsModelSerializer
    permission_classes = [permissions.OnlyBaseUser, ]

    def get_object(self):
        return self.request.user.base_user.fund_settings


# For Loan Receive Start


class CreditLoanReceiveRecordListAPIView(CreditFundListAPIView):

    serializer_class = serializers.CreditFundForLoanRecieveModelSerializer

    def get_queryset(self):
        if BaseUserModel.objects.filter(base_user=self.request.user).exists():
            return self.request.user.base_user.credit_funds.filter(
                added__year=datetime.datetime.today().year,
                is_deleted=False
                )
        elif SubUserModel.objects.filter(root_user=self.request.user).exists():
            return self.request.user.root_sub_user.base_user.credit_funds.filter(
                added__year=datetime.datetime.today().year,
                is_deleted=False
                )


class CreditLoanReceiveRecordListCreateAPIView(CreditFundListCreateAPIView):

    serializer_class = serializers.CreditFundForLoanRecieveModelSerializer

    def get_queryset(self):
        return self.request.user.base_user.credit_funds.all().filter(
            added__year=datetime.datetime.today().year,
            is_deleted=False,
            is_refundable=False,
            is_returnable=True
        )


class CreditLoanReceiveRecordRetrieveUpdateAPIView(CreditFundRetrieveUpdateAPIView):

    serializer_class = serializers.CreditFundForLoanRecieveModelSerializer

    def get_queryset(self):
        return self.request.user.base_user.credit_funds.filter(
            is_deleted=False,
            is_refundable=False,
            is_returnable=True
            )


class CreditLoanReceiveRecordRetrieveAPIView(CreditFundRetrieveAPIView):

    serializer_class = serializers.CreditFundForLoanRecieveModelSerializer

    def get_queryset(self):
        return self.request.user.base_user.credit_funds.filter(
            is_deleted=False,
            is_refundable=False,
            is_returnable=True
            )


# For Loan Receive End


class CreditFundHistory(generics.ListAPIView):
    serializer_class = serializers.CreditFundHistoryModelSerializer
    permission_classes = [permissions.BaseUserOrSubUser, ]
    filter_backends = (filters.OrderingFilter, filters.SearchFilter)
    search_fields = (
        'action_by__username',
        'description',
        'old_uuid',
        'credit_fund__source__source_name',
        'old_description',
        'new_description',
        'old_amount',
        'new_amount'
    )
    ordering_fields = ()
    ordering = ('-id',)

    def get_queryset(self):
        return utils.get_base_user(self.request).all_expenditure_records_history.all()


class CreditFundSourceHistory(generics.ListAPIView):
    serializer_class = serializers.CreditFundSourceHistoryModelSerializer
    permission_classes = [permissions.OnlyBaseUser, ]

    def get_queryset(self):
        return self.request.user.base_user.all_credit_fund_source_histories.all()


class CreditFundGenCSVEmail(CreditFundListAPIView):
    today = datetime.datetime.today().strftime("%d %B, %Y")
    headings = ['Source Name', 'Record Added Time', 'Fund Added Time', 'Amount']
    attributes = ['source', 'added', 'fund_added', 'amount']

    def get(self, request, *args, **kwargs):
        items = self.filter_queryset(queryset=self.get_queryset())
        print(items)
        file_name = f'credit_fund_list_{self.today}.csv'
        response = utils.django_download_generated_csv_from_model_object(
            file_name=file_name,
            query_set=items,
            headings=self.headings,
            attributes=self.attributes
        )
        subject = f'Accounts Application: {self.today} Report of Credit Fund'
        body = f'This is an automated email from your application.'
        from_email = os.environ.get('EMAIL')
        base_user = items.first().base_user

        emails = base_user.all_emails.filter(is_active=True)

        to = [base_user.base_user.email, ]

        for email in emails:
            to.append(email.email_address)

        utils.django_send_email_with_attachments(
            subject=subject,
            body=body,
            from_email=from_email,
            to=to,
            file_name=file_name,
            content=response.getvalue(),
            mimetype='text/csv'
        )

        return response


class CreditExportPDFReport(CreditFundGenCSVEmail):

    def get(self, request, *args, **kwargs):
        items = self.filter_queryset(queryset=self.get_queryset())
        row_values = [[obj.__getattribute__(name) for name in self.attributes] for obj in items]
        amounts = [obj.amount for obj in items]
        context = {
            'headings': self.headings,
            'row_values': row_values,
            'attributes': self.attributes,
            'pdf_name': f'Credit_Report_{self.today}',
            'company': CompanyInfoModel.objects.get(base_user=items.first().base_user),
            'sum': utils.sum_int_of_array(amounts),
            'date': datetime.datetime.now(),
            'page_unique_id': uuid.uuid4()
        }
        response = utils.django_render_to_pdf('credit_report_pdf_template.html', context)
        return response
