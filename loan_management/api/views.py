from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from project import permissions as main_permissions
from loan_management.api import serializers as loan_serializers
from base_user.models import BaseUserModel
from sub_user.models import SubUserModel
from credit.api.filters import CreditFundFilter
from expenditure.api.filters import ExpenditureRecordFilter


class LoanCreditListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [main_permissions.FundIsNotLocked, main_permissions.OnlyBaseUser]
    serializer_class = loan_serializers.CreditForLoanSerializer
    filter_backends = (filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend)
    search_fields = ('description', 'uuid')
    ordering_fields = ('added', 'source__source_name', 'amount')
    ordering = ('-id', )
    filterset_class = CreditFundFilter

    def request_data(self):
        return self.request

    def logged_in_user(self):
        return self.request_data().user

    def base_user_model(self):
        base_user = BaseUserModel.objects.filter(base_user=self.logged_in_user())
        sub_user = SubUserModel.objects.filter(root_user=self.logged_in_user())

        if base_user.exists():
            return self.logged_in_user().base_user
        if sub_user.exists():
            return self.logged_in_user().root_sub_user.base_user

    def get_queryset(self):
        return self.base_user_model().credit_funds.filter(is_refundable=True)


class LoanCreditListAPIView(generics.ListAPIView):
    permission_classes = [main_permissions.FundIsNotLocked, main_permissions.BaseUserOrSubUser, main_permissions.SubUserCanList]
    serializer_class = loan_serializers.CreditForLoanSerializer
    filter_backends = (filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend)
    search_fields = ('description', 'uuid')
    ordering_fields = ('added', 'source__source_name', 'amount')
    ordering = ('-id', )
    filterset_class = CreditFundFilter

    def request_data(self):
        return self.request

    def logged_in_user(self):
        return self.request_data().user

    def base_user_model(self):
        base_user = BaseUserModel.objects.filter(base_user=self.logged_in_user())
        sub_user = SubUserModel.objects.filter(root_user=self.logged_in_user())

        if base_user.exists():
            return self.logged_in_user().base_user
        if sub_user.exists():
            return self.logged_in_user().root_sub_user.base_user

    def get_queryset(self):
        return self.base_user_model().credit_funds.filter(is_refundable=True)


class LoanExpenditureListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [main_permissions.FundIsNotLocked, main_permissions.BaseUserOrSubUser, main_permissions.SubUserCanAdd]
    serializer_class = loan_serializers.ExpenditureForLoanSerializer
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

    def request_data(self):
        return self.request

    def logged_in_user(self):
        return self.request_data().user

    def base_user_model(self):
        base_user = BaseUserModel.objects.filter(base_user=self.logged_in_user())
        sub_user = SubUserModel.objects.filter(root_user=self.logged_in_user())

        if base_user.exists():
            return self.logged_in_user().base_user
        if sub_user.exists():
            return self.logged_in_user().root_sub_user.base_user

    def get_queryset(self):
        return self.base_user_model().all_expenditure_records.filter(is_for_refund=True, is_deleted=False)


class LoanExpenditureListAPIView(generics.ListAPIView):
    permission_classes = [main_permissions.FundIsNotLocked, main_permissions.BaseUserOrSubUser, main_permissions.SubUserCanList]
    serializer_class = loan_serializers.ExpenditureForLoanSerializer
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

    def request_data(self):
        return self.request

    def logged_in_user(self):
        return self.request_data().user

    def base_user_model(self):
        base_user = BaseUserModel.objects.filter(base_user=self.logged_in_user())
        sub_user = SubUserModel.objects.filter(root_user=self.logged_in_user())

        if base_user.exists():
            return self.logged_in_user().base_user
        if sub_user.exists():
            return self.logged_in_user().root_sub_user.base_user

    def get_queryset(self):
        return self.base_user_model().all_expenditure_records.filter(is_for_refund=True, is_deleted=False)


class LoanCreditUpdateAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [main_permissions.FundIsNotLocked, main_permissions.OnlyBaseUser]
    serializer_class = loan_serializers.CreditForLoanSerializer
    lookup_field = 'uuid'

    def request_data(self):
        return self.request

    def logged_in_user(self):
        return self.request_data().user

    def base_user_model(self):
        base_user = BaseUserModel.objects.filter(base_user=self.logged_in_user())
        sub_user = SubUserModel.objects.filter(root_user=self.logged_in_user())

        if base_user.exists():
            return self.logged_in_user().base_user
        if sub_user.exists():
            return self.logged_in_user().root_sub_user.base_user

    def get_queryset(self):
        return self.base_user_model().credit_funds.filter(is_refundable=True)


class LoanExpenditureUpdateAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [main_permissions.FundIsNotLocked, main_permissions.OnlyBaseUser]
    serializer_class = loan_serializers.ExpenditureForLoanSerializer
    lookup_field = "uuid"

    def request_data(self):
        return self.request

    def logged_in_user(self):
        return self.request_data().user

    def base_user_model(self):
        base_user = BaseUserModel.objects.filter(base_user=self.logged_in_user())
        sub_user = SubUserModel.objects.filter(root_user=self.logged_in_user())

        if base_user.exists():
            return self.logged_in_user().base_user
        if sub_user.exists():
            return self.logged_in_user().root_sub_user.base_user

    def get_queryset(self):
        return self.base_user_model().all_expenditure_records.filter(is_for_refund=True, is_deleted=False)

