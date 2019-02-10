from rest_framework import generics
from base_user.models import BaseUserModel
from sub_user.models import SubUserModel
import datetime


class DownloadReportPDF(generics.ListAPIView):

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
    
    def get_todays_open_debit_amount(self):
        expend_obj_non_ref_and_non_ret = self.get_expend_records().filter(
            Q(is_verified=True),
            Q(expend_date__lt=datetime.date.today()),
            Q(is_for_refund=False),
            Q(is_for_return=False)
            )
        all_expend_amounts = [obj.amount for obj in expend_obj_non_ref_and_non_ret]

        todays_open_debit_amount = utils.sum_int_of_array(all_expend_amounts)

        return todays_open_debit_amount
    
    def get_today_credit_fund(self):
        expend_obj_ref_or_ret = self.get_expend_records().filter(
            Q(is_verified=True),
            Q(expend_date=datetime.date.today()),
            Q(is_for_refund=True) | Q(is_for_return=True)
            )

        credit_obj = self.get_credit_funds().filter(
            Q(fund_added=datetime.date.today())
            )

        all_expend_amounts = [obj.amount for obj in expend_obj_ref_or_ret]
        all_credit_amounts = [obj.amount for obj in credit_obj]

        total_expend_amount = utils.sum_int_of_array(all_expend_amounts)
        total_credit_amount = utils.sum_int_of_array(all_credit_amounts)

        todays_open_credit_fund = total_credit_amount - total_expend_amount

        return todays_open_credit_fund
    
    def get_today_debit_amount(self):
        expend_obj_non_ref_and_non_ret = self.get_expend_records().filter(
            Q(is_verified=True),
            Q(expend_date=datetime.date.today()),
            Q(is_for_refund=False),
            Q(is_for_return=False)
            )
        all_expend_amounts = [obj.amount for obj in expend_obj_non_ref_and_non_ret]

        todays_open_debit_amount = utils.sum_int_of_array(all_expend_amounts)

        return todays_open_debit_amount
