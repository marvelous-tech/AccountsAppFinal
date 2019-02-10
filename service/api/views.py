from django.db.models import Q
from rest_framework import generics
from rest_framework.response import Response
from drf_multiple_model.views import FlatMultipleModelAPIView
from credit.api.serializers import CreditFundHistoryModelSerializer
from expenditure.api.serializers import ExpenditureRecordHistoryModelSerializer
from base_user.models import BaseUserModel
from sub_user.models import SubUserModel
from base_user.api.serializers import BaseUserSerializer
from sub_user.api.serializers import SubUserModelSerializers
from project.permissions import BaseUserOrSubUser, OnlyBaseUser, BaseUserOrSubUserInfoPermission
from utils import utils
import os
import datetime


class GetUserData(generics.RetrieveAPIView):
    permission_classes = [BaseUserOrSubUserInfoPermission, ]

    def get_object(self):
        queryset = None
        if BaseUserModel.objects.filter(base_user=self.request.user).exists():
            queryset = self.request.user.base_user
        elif SubUserModel.objects.filter(root_user=self.request.user).exists():
            queryset = self.request.user.root_sub_user
        return queryset
    
    def get_serializer_class(self):
        if BaseUserModel.objects.filter(base_user=self.request.user).exists():
            return BaseUserSerializer
        elif SubUserModel.objects.filter(root_user=self.request.user).exists():
            return SubUserModelSerializers


class GetTotalFundAmount(generics.GenericAPIView):
    permission_classes = [BaseUserOrSubUserInfoPermission, ]

    def get_queryset(self):
        if BaseUserModel.objects.filter(base_user=self.request.user).exists():
            return self.request.user.base_user.credit_funds.filter(is_deleted=False)
        elif SubUserModel.objects.filter(root_user=self.request.user).exists():
            return self.request.user.root_sub_user.base_user.credit_funds.filter(is_deleted=False)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        all_amounts = []

        for instance in queryset:
            all_amounts.append(instance.amount)
        
        total = utils.sum_int_of_array(all_amounts)

        return Response({'total_fund_amount': total})


class MailOnWrongPassword(generics.GenericAPIView):
    permission_classes = [OnlyBaseUser, ]

    def get_base_user(self):
        if BaseUserModel.objects.filter(base_user=self.request.user).exists():
            return self.request.user.base_user
        elif SubUserModel.objects.filter(root_user=self.request.user).exists():
            return self.request.user.root_sub_user.base_user

    def get(self, request, *args, **kwargs):
        
        subject = "Account Application: Malicious login."
        body = "Did you just wanted to change your Fund Settings? We refused that request. The person who is trying to login entered wrong password. If the person is not you please immediate contact us to overcome this issue or change your password now."
        from_email = os.environ.get('EMAIL')

        base_user = self.get_base_user()

        emails = base_user.all_emails.filter(is_active=True)
        to = [base_user.base_user.email, ]

        for email in emails:
            to.append(email.email_address)

        utils.django_send_email(subject=subject, body=body, from_email=from_email, to=to)

        return Response({"An email was sent to the admin about this situation."})


class MailOnNonBaseUser(generics.GenericAPIView):
    permission_classes = [BaseUserOrSubUser, ]

    def get_base_user(self):
        if BaseUserModel.objects.filter(base_user=self.request.user).exists():
            return self.request.user.base_user
        elif SubUserModel.objects.filter(root_user=self.request.user).exists():
            return self.request.user.root_sub_user.base_user

    def get(self, request, *args, **kwargs):
        
        subject = "Account Application: A non authorizer login."
        body = "A non authorizer account is trying to change the Fund Settings. We refused that request."
        from_email = os.environ.get('EMAIL')
        base_user = self.get_base_user()

        emails = base_user.all_emails.filter(is_active=True)
        to = [base_user.base_user.email, ]

        for email in emails:
            to.append(email.email_address)

        if BaseUserModel.objects.filter(base_user=request.user).exists():
            to.append(request.user.email)
        elif SubUserModel.objects.filter(root_user=request.user).exists():
            to.append(request.user.root_sub_user.base_user.base_user.email)

        utils.django_send_email(subject=subject, body=body, from_email=from_email, to=to)

        return Response({"An email was sent to the admin about this situation."})


class GrabWhatYouWantedAPIView(generics.GenericAPIView):
    permission_classes = [BaseUserOrSubUserInfoPermission, ]

    def get_base_user(self):
        if BaseUserModel.objects.filter(base_user=self.request.user).exists():
            return self.request.user.base_user
        elif SubUserModel.objects.filter(root_user=self.request.user).exists():
            return self.request.user.root_sub_user.base_user
    
    def is_base_user(self):
        return BaseUserModel.objects.filter(base_user=self.request.user).exists()

    def is_sub_user(self):
        return SubUserModel.objects.filter(root_user=self.request.user).exists()

    def get_credit_funds(self):
        return self.get_base_user().credit_funds.filter(is_deleted=False)
    
    def get_expend_records(self):
        return self.get_base_user().all_expenditure_records.filter(is_deleted=False)
    
    def get_user_permissions(self):
        if self.is_base_user():
            return {
                'canAdd': True,
                'canEdit': True,
                'canList': True,
                'canRetrieve': True,
                'canFundSourceListCreate': True,
                'canFundSourceEdit': True,
                'is_active': True,
                'user_type': 'admin'
            }
        elif self.is_sub_user():
            return {
                'canAdd': self.request.user.root_sub_user.canAdd,
                'canEdit': self.request.user.root_sub_user.canEdit,
                'canList': self.request.user.root_sub_user.canList,
                'canRetrieve': self.request.user.root_sub_user.canRetrieve,
                'canFundSourceListCreate': False,
                'canFundSourceEdit': False,
                'is_active': self.request.user.root_sub_user.is_active,
                'user_type': self.request.user.root_sub_user.user_type
            }
    
    def get_account_status(self):
        info = self.request.user.user_extra_info
        return {
            'is_approved': info.is_approved,
            'is_locked': info.is_not_locked is False,
            'is_active': info.is_active
        }
    # %Y-%m-%d

    def get_todays_open_credit_fund(self):
        expend_obj_ref_or_ret = self.get_expend_records().filter(
            Q(is_verified=True),
            Q(expend_date__lt=datetime.date.today()),
            Q(is_for_refund=True) | Q(is_for_return=True)
            )

        credit_obj = self.get_credit_funds().filter(
            Q(fund_added__lt=datetime.date.today())
            )

        all_expend_amounts = [obj.amount for obj in expend_obj_ref_or_ret]
        all_credit_amounts = [obj.amount for obj in credit_obj]

        total_expend_amount = utils.sum_int_of_array(all_expend_amounts)
        total_credit_amount = utils.sum_int_of_array(all_credit_amounts)

        todays_open_credit_fund = total_credit_amount - total_expend_amount

        return todays_open_credit_fund
    
    def get_remaining_credit_fund_amount(self):

        expend_obj = self.get_expend_records().filter(Q(is_verified=True))
        credit_obj = self.get_credit_funds().filter()

        all_expend_obj_amounts = [obj.amount for obj in expend_obj]
        all_credit_obj_amounts = [obj.amount for obj in credit_obj]

        total_expend_amount = utils.sum_int_of_array(all_expend_obj_amounts)
        total_credit_amount = utils.sum_int_of_array(all_credit_obj_amounts)

        remaining_credit_fund_amount = total_credit_amount - total_expend_amount

        return remaining_credit_fund_amount
    
    def get_this_month_total_expend_amount(self):
        expend_obj_non_ref_and_non_ret = self.get_expend_records().filter(
            Q(is_verified=True),
            Q(expend_date__year=datetime.datetime.now().year),
            Q(expend_date__month=datetime.datetime.now().month),
            Q(is_for_refund=False),
            Q(is_for_return=False)
            )
        all_expend_amounts = [obj.amount for obj in expend_obj_non_ref_and_non_ret]

        this_month_total_expend_amount = utils.sum_int_of_array(all_expend_amounts)

        return this_month_total_expend_amount
    
    def get_total_unauthorized_expend_amount(self):

        unauthorized_expend_records = self.get_expend_records().filter(Q(is_verified=False))

        unauthorized_expend_records_amounts = [obj.amount for obj in unauthorized_expend_records]
        total_unauthorized_expend_amount = utils.sum_int_of_array(unauthorized_expend_records_amounts)

        return total_unauthorized_expend_amount
    
    def get_fund_status(self):
        return self.get_base_user().fund_settings.is_not_locked
    
    def get_total_credit_fund_amount(self):

        # Todo: Check if this algorithm has a mathmetical error in total credit amount

        expend_obj_ref_or_ret = self.get_expend_records().filter(
            Q(is_verified=True),
            Q(is_for_refund=True) | Q(is_for_return=True)
            )

        credit_obj = self.get_credit_funds().filter(
            Q(fund_added__year=datetime.datetime.now().year)
            )
        all_expend_amounts = [obj.amount for obj in expend_obj_ref_or_ret]
        all_credit_amounts = [obj.amount for obj in credit_obj]

        total_expend_amount = utils.sum_int_of_array(all_expend_amounts)
        total_credit_amount = utils.sum_int_of_array(all_credit_amounts)

        total_credit_fund_amount = total_credit_amount - total_expend_amount

        return total_credit_fund_amount

    # new 
    def get_this_year_total_expend_amount(self):

        # Todo: Check if this algorithm has a mathmetical error in total credit amount

        expend_obj_non_ref_and_non_ret = self.get_expend_records().filter(
            Q(is_verified=True),
            Q(expend_date__year=datetime.datetime.now().year),
            Q(is_for_refund=False),
            Q(is_for_return=False)
            )

        all_expend_amounts = [obj.amount for obj in expend_obj_non_ref_and_non_ret]

        this_year_total_expend_amount = utils.sum_int_of_array(all_expend_amounts)

        return this_year_total_expend_amount
    
    def get_this_year_remaining_credit_fund_amount(self):

        # Todo: Check if this algorithm has a mathmetical error in total credit amount

        expend_obj = self.get_expend_records().filter(
            Q(expend_date__year=datetime.datetime.now().year),
            Q(is_verified=True)
            )

        credit_obj = self.get_credit_funds().filter(
            Q(fund_added__year=datetime.datetime.now().year)
            )

        all_expend_amounts = [obj.amount for obj in expend_obj]
        all_credit_amounts = [obj.amount for obj in credit_obj]

        this_year_total_expend_amount = utils.sum_int_of_array(all_expend_amounts)
        this_year_total_credit_amount = utils.sum_int_of_array(all_credit_amounts)

        this_year_remaining_credit_fund_amount = this_year_total_credit_amount - this_year_total_expend_amount

        return this_year_remaining_credit_fund_amount
    
    def get_this_year_total_credit_fund_amount(self):  # OK

        # Todo: Check if this algorithm has a mathmetical error in total credit amount

        expend_obj_ref_or_ret = self.get_expend_records().filter(
            Q(is_verified=True),
            Q(expend_date__year=datetime.datetime.now().year),
            Q(is_for_refund=True) | Q(is_for_return=True)
            )

        credit_obj = self.get_credit_funds().filter(
            Q(fund_added__year=datetime.datetime.now().year)
            )
        all_expend_amounts = [obj.amount for obj in expend_obj_ref_or_ret]
        all_credit_amounts = [obj.amount for obj in credit_obj]

        this_year_total_expend_amount = utils.sum_int_of_array(all_expend_amounts)
        this_year_total_credit_amount = utils.sum_int_of_array(all_credit_amounts)

        this_year_total_credit_fund_amount = this_year_total_credit_amount - this_year_total_expend_amount

        return this_year_total_credit_fund_amount
    
    def get_this_month_total_credit_fund_amount(self):

        # Todo: Check if this algorithm has a mathmetical error in total credit amount

        expend_obj_ref_or_ret = self.get_expend_records().filter(
            Q(is_verified=True),
            Q(expend_date__year=datetime.datetime.now().year),
            Q(expend_date__month=datetime.datetime.now().month),
            Q(is_for_refund=True) | Q(is_for_return=True)
            )

        credit_obj = self.get_credit_funds().filter(
            Q(fund_added__year=datetime.datetime.now().year),
            Q(fund_added__month=datetime.datetime.now().month)
            )
        all_expend_amounts = [obj.amount for obj in expend_obj_ref_or_ret]
        all_credit_amounts = [obj.amount for obj in credit_obj]

        this_month_total_expend_amount = utils.sum_int_of_array(all_expend_amounts)
        this_month_total_credit_amount = utils.sum_int_of_array(all_credit_amounts)

        this_month_total_credit_fund_amount = this_month_total_credit_amount - this_month_total_expend_amount

        return this_month_total_credit_fund_amount
    
    def get_this_year_total_unauthorized_expend_amount(self):
        unauthorized_expend_records = self.get_expend_records().filter(
            Q(expend_date__year=datetime.datetime.now().year),
            Q(is_verified=False)
            )
        unauthorized_expend_records_amounts = [obj.amount for obj in unauthorized_expend_records]
        this_year_total_unauthorized_expend_amount = utils.sum_int_of_array(unauthorized_expend_records_amounts)

        return this_year_total_unauthorized_expend_amount
    
    def get(self, request, *args, **kwargs):
        context = {
            'is_base_user': self.is_base_user(),
            'is_sub_user': self.is_sub_user(),
            'user_permissions': self.get_user_permissions(),
            'account_status': self.get_account_status(),
            'todays_open_credit_fund': self.get_todays_open_credit_fund(),
            'remaining_credit_fund_amount': self.get_remaining_credit_fund_amount(),
            'this_month_total_expend_amount': self.get_this_month_total_expend_amount(),
            'total_unauthorized_expend_amount': self.get_total_unauthorized_expend_amount(),
            'total_credit_fund_amount': self.get_total_credit_fund_amount(),
            'fund_status': self.get_fund_status(),

            "this_year_total_expend_amoun": self.get_this_year_total_expend_amount(),
            "this_year_remaining_credit_fund_amount": self.get_this_year_remaining_credit_fund_amount(),
            "this_year_total_credit_fund_amount": self.get_this_year_total_credit_fund_amount(),
            "this_year_total_unauthorized_expend_amount": self.get_this_year_total_unauthorized_expend_amount(),
            "this_month_total_credit_fund_amount": self.get_this_month_total_credit_fund_amount(),

            "this_year": datetime.datetime.now().year
        }
        return Response(context)


class CreditExpenditureHistoryAPIView(FlatMultipleModelAPIView):
    permission_classes = [OnlyBaseUser, ]
    sorting_fields = ['-added', ]

    def get_querylist(self):
        return [
            {
                'queryset': self.request.user.base_user.all_credit_fund_histories.all(),
                'serializer_class': CreditFundHistoryModelSerializer
            },
            {
                'queryset': self.request.user.base_user.all_expenditure_records_history.all(),
                'serializer_class': ExpenditureRecordHistoryModelSerializer
            }
        ]

