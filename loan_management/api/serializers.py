from rest_framework import serializers
from loan_management import models as loan_models
from credit.api import serializers as credit_serializers
from expenditure.api import serializers as expend_serializers
from utils import utils
import uuid
from expenditure import models as expend_models
from credit import models as credit_models


class CreditFundOnLoanModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = loan_models.CreditFundOnLoanModel
        fields = '__all__'
        read_only_fields = ('base_user', 'credit_fund')


class ExpenditureRecordOnLoanModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = loan_models.ExpenditureRecordOnLoanModel
        fields = '__all__'
        read_only_fields = ('base_user', 'expenditure_record_model')


class CreditForLoanSerializer(credit_serializers.CreditFundModelSerializer):
    loan = CreditFundOnLoanModelSerializer(many=False, read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name="loan-app:credit-update", lookup_field='uuid')

    class Meta:
        model = credit_models.CreditFundModel
        fields = (
            'source',
            'source_name',
            'url',
            'description',
            'added',
            'updated',
            'amount',
            'fund_added',
            'uuid',
            'is_deleted',
            'extra_description',
            'loan',
            'is_refundable'
        )
        read_only_fields = ('uuid', 'added', 'updated', 'source_name', 'is_refundable', 'loan')

    def create(self, validated_data):
        validated_data.pop("extra_description")
        validated_data.pop("is_deleted")
        obj = credit_models.CreditFundModel.objects.create(
            base_user=self.base_user_model(),
            uuid=uuid.uuid4(),
            is_deleted=False,
            is_refundable=True,
            **validated_data
        )
        loan_models.CreditFundOnLoanModel.objects.create(
            base_user=self.base_user_model(),
            credit_fund=obj
        )
        return obj

    def update(self, instance, validated_data):

        if instance.is_deleted is True and validated_data.get('is_deleted') is False:
            # Todo: add history with is_restored = True
            credit_models.CreditFundHistoryModel.objects.create(
                action_by=self.logged_in_user(),
                base_user=self.base_user_model(),
                credit_fund=instance,
                is_deleted=False,
                is_updated=False,
                is_restored=True,
                old_source=instance.source,
                new_source=validated_data.get('source'),
                old_description=instance.description,
                new_description=validated_data.get('description'),
                old_fund_added=instance.fund_added,
                new_fund_added=validated_data.get('fund_added'),
                old_amount=instance.amount,
                new_amount=validated_data.get('amount'),
                description=validated_data.get('extra_description'),
                old_uuid=instance.uuid,
            )
            instance.is_deleted = False
            instance.save()
            return instance

        if instance.is_deleted is False and validated_data.get('is_deleted') is True:
            # Todo: add history with is_deleted = True
            raw_value = instance.amount
            print(raw_value)

            expend_obj_non_ref = self.base_user_model().all_expenditure_records.all().filter(
                is_for_refund=False,
                is_deleted=False)
            expend_obj_ref = self.base_user_model().all_expenditure_records.all().filter(
                is_for_refund=True,
                is_deleted=False)
            credit_fund_obj = self.base_user_model().credit_funds.filter(is_deleted=False)

            all_credit_fund_amounts = [obj.amount for obj in credit_fund_obj]
            all_record_amounts_ref = [obj.amount for obj in expend_obj_ref]
            all_record_amounts_non_ref = [obj.amount for obj in expend_obj_non_ref]

            total_pre_credit_fund_amount = utils.sum_int_of_array(all_credit_fund_amounts)
            total_pre_record_amount_non_ref = utils.sum_int_of_array(all_record_amounts_non_ref)
            total_pre_record_amount_ref = utils.sum_int_of_array(all_record_amounts_ref)

            print(total_pre_credit_fund_amount, total_pre_record_amount_non_ref, total_pre_record_amount_ref)

            real_asset = total_pre_credit_fund_amount - total_pre_record_amount_ref - raw_value

            print(real_asset)

            if real_asset >= total_pre_record_amount_non_ref:
                credit_models.CreditFundHistoryModel.objects.create(
                    action_by=self.logged_in_user(),
                    base_user=self.base_user_model(),
                    credit_fund=instance,
                    is_deleted=True,
                    is_updated=False,
                    is_restored=False,
                    old_source=instance.source,
                    new_source=validated_data.get('source'),
                    old_description=instance.description,
                    new_description=validated_data.get('description'),
                    old_fund_added=instance.fund_added,
                    new_fund_added=validated_data.get('fund_added'),
                    old_amount=instance.amount,
                    new_amount=validated_data.get('amount'),
                    description=validated_data.get('extra_description'),
                    old_uuid=instance.uuid,
                )
                instance.is_deleted = True
                instance.save()

                if instance:
                    return instance
                raise serializers.ValidationError("Not found!")
            raise serializers.ValidationError("Credits will be lower than your debits!")
        raw_value = instance.amount
        new_value = validated_data.get('amount', raw_value)
        expend_obj_non_ref = self.base_user_model().all_expenditure_records.all().filter(
            is_for_refund=False,
            is_deleted=False)
        expend_obj_ref = self.base_user_model().all_expenditure_records.all().filter(
            is_for_refund=True,
            is_deleted=False)
        credit_fund_obj = self.base_user_model().credit_funds.all()

        all_credit_fund_amounts = [obj.amount for obj in credit_fund_obj]
        all_record_amounts_ref = [obj.amount for obj in expend_obj_ref]
        all_record_amounts_non_ref = [obj.amount for obj in expend_obj_non_ref]

        total_pre_credit_fund_amount = utils.sum_int_of_array(all_credit_fund_amounts)
        total_pre_record_amount_non_ref = utils.sum_int_of_array(all_record_amounts_non_ref)
        total_pre_record_amount_ref = utils.sum_int_of_array(all_record_amounts_ref)

        real_asset = total_pre_credit_fund_amount - total_pre_record_amount_ref - raw_value + new_value

        if real_asset >= total_pre_record_amount_non_ref:
            # Todo: add history with is_updated = True
            credit_models.CreditFundHistoryModel.objects.create(
                action_by=self.logged_in_user(),
                base_user=self.base_user_model(),
                credit_fund=instance,
                is_deleted=False,
                is_updated=True,
                is_restored=False,
                old_source=instance.source,
                new_source=validated_data.get('source'),
                old_description=instance.description,
                new_description=validated_data.get('description'),
                old_fund_added=instance.fund_added,
                new_fund_added=validated_data.get('fund_added'),
                old_amount=instance.amount,
                new_amount=validated_data.get('amount'),
                description=validated_data.get('extra_description'),
                old_uuid=instance.uuid,
            )
            instance.source = validated_data.get('source', instance.source)
            instance.description = validated_data.get('description', instance.description)
            instance.amount = validated_data.get('amount', instance.amount)
            instance.fund_added = validated_data.get('fund_added', instance.fund_added)

            instance.save()

            return instance

        raise serializers.ValidationError(detail="Total credit will be lower than total debit!")


class ExpenditureForLoanSerializer(expend_serializers.ExpenditureRecordModelSafeSerializer):
    loan = ExpenditureRecordOnLoanModelSerializer(many=False, read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name="loan-app:expend-update", lookup_field='uuid')
    details_url = None
    edit_url = None

    class Meta:
        model = expend_models.ExpenditureRecordModel
        exclude = ('base_user', )
        read_only_fields = ('uuid', 'added_by', 'added', 'updated', 'is_for_refund', 'loan')

    def create(self, validated_data):
        validated_data.pop('extra_description')
        new_value = validated_data.get('amount')
        expend_obj_non_ref = self.base_user_model().all_expenditure_records.all().filter(
                                                                                         is_for_refund=False,
                                                                                         is_deleted=False)
        expend_obj_ref = self.base_user_model().all_expenditure_records.all().filter(
                                                                                     is_for_refund=True,
                                                                                     is_deleted=False)
        credit_fund_obj = self.base_user_model().credit_funds.filter(is_deleted=False)
        only_refundable_credit = self.base_user_model().credit_funds.filter(is_deleted=False, is_refundable=True)

        all_credit_fund_amounts = [obj.amount for obj in credit_fund_obj]
        all_credit_fund_amounts_ref = [obj.amount for obj in only_refundable_credit]
        all_record_amounts_ref = [obj.amount for obj in expend_obj_ref]
        all_record_amounts_non_ref = [obj.amount for obj in expend_obj_non_ref]

        all_credit_fund_amounts_ref_amount = utils.sum_int_of_array(all_credit_fund_amounts_ref)
        total_pre_credit_fund_amount = utils.sum_int_of_array(all_credit_fund_amounts)
        total_pre_record_amount_non_ref = utils.sum_int_of_array(all_record_amounts_non_ref)
        total_pre_record_amount_ref = utils.sum_int_of_array(all_record_amounts_ref)

        final_ref_expand = total_pre_record_amount_ref + new_value

        final_non_ref_expend = total_pre_record_amount_non_ref + new_value

        real_asset = total_pre_credit_fund_amount - total_pre_record_amount_ref

        if real_asset >= final_non_ref_expend and all_credit_fund_amounts_ref_amount >= final_ref_expand:
            obj = expend_models.ExpenditureRecordModel.objects.create(
                added_by=self.logged_in_user(),
                base_user=self.base_user_model(),
                uuid=uuid.uuid4(),
                is_for_refund=True,
                **validated_data
            )
            loan_models.ExpenditureRecordOnLoanModel.objects.create(
                base_user=self.base_user_model(),
                expenditure_record_model=obj
            )
            return obj
        raise serializers.ValidationError(detail='''Credit Loan will be exceed! So you cannot add 
        any more records. After authority add more Credit Loan in Database you can entry more records.''')

    def update(self, instance, validated_data):
        if instance.is_deleted is False and validated_data.get('is_deleted') is True:
            instance.is_deleted = True
            # Todo: add history with is_deleted = True
            expend_models.ExpenditureRecordHistoryModel.objects.create(
                action_by=self.logged_in_user(),
                base_user=self.base_user_model(),
                related_records=instance,
                old_expend_heading=instance.expend_heading,
                new_expend_heading=instance.expend_heading,
                old_expend_by=instance.expend_by,
                new_expend_by=instance.expend_by,
                old_description=instance.description,
                new_description=instance.description,
                old_amount=instance.amount,
                new_amount=instance.amount,
                old_is_verified=instance.is_verified,
                new_is_verified=instance.is_verified,
                old_expend_date=instance.expend_date,
                new_expend_date=instance.expend_date,
                old_uuid=instance.uuid,
                is_updated=False,
                is_deleted=True,
                is_restored=False,
                description=validated_data.get('extra_description'),
            )
            instance.save()
            return instance
        if instance.is_deleted is True and validated_data.get('is_deleted') is False:
            # Todo: add history with is_restore = True
            raw_amount = instance.amount
            expend_obj_non_ref = self.base_user_model().all_expenditure_records.all().filter(
                is_for_refund=False,
                is_deleted=False)
            expend_obj_ref = self.base_user_model().all_expenditure_records.all().filter(
                is_for_refund=True,
                is_deleted=False)
            credit_fund_obj = self.base_user_model().credit_funds.filter(is_deleted=False)

            all_credit_fund_amounts = [obj.amount for obj in credit_fund_obj]
            all_record_amounts_ref = [obj.amount for obj in expend_obj_ref]
            all_record_amounts_non_ref = [obj.amount for obj in expend_obj_non_ref]

            total_pre_credit_fund_amount = utils.sum_int_of_array(all_credit_fund_amounts)
            total_pre_record_amount_non_ref = utils.sum_int_of_array(all_record_amounts_non_ref)
            total_pre_record_amount_ref = utils.sum_int_of_array(all_record_amounts_ref)

            final_value_after_delete = total_pre_record_amount_non_ref - raw_amount

            real_asset = total_pre_credit_fund_amount - total_pre_record_amount_ref

            if real_asset >= final_value_after_delete:
                instance.is_deleted = False
                expend_models.ExpenditureRecordHistoryModel.objects.create(
                    action_by=self.logged_in_user(),
                    base_user=self.base_user_model(),
                    related_records=instance,
                    old_expend_heading=instance.expend_heading,
                    new_expend_heading=instance.expend_heading,
                    old_expend_by=instance.expend_by,
                    new_expend_by=instance.expend_by,
                    old_description=instance.description,
                    new_description=instance.description,
                    old_amount=instance.amount,
                    new_amount=instance.amount,
                    old_is_verified=instance.is_verified,
                    new_is_verified=instance.is_verified,
                    old_expend_date=instance.expend_date,
                    new_expend_date=instance.expend_date,
                    old_uuid=instance.uuid,
                    is_updated=False,
                    is_deleted=False,
                    is_restored=True,
                    description=validated_data.get('extra_description'),
                )
                instance.save()
                return instance
            raise serializers.ValidationError(
                detail='Credit Fund will be exceede! So you cannot add any more records. After authority add more Credit Fund in Database you can entry more records.')
        if instance.is_verified is True and validated_data.get('is_verified') is False:
            # Todo: add history with is_updated = True
            expend_models.ExpenditureRecordHistoryModel.objects.create(
                action_by=self.logged_in_user(),
                base_user=self.base_user_model(),
                related_records=instance,
                old_expend_heading=instance.expend_heading,
                new_expend_heading=validated_data.get('expend_heading'),
                old_expend_by=instance.expend_by,
                new_expend_by=validated_data.get('expend_by'),
                old_description=instance.description,
                new_description=validated_data.get('description'),
                old_amount=instance.amount,
                new_amount=validated_data.get('amount'),
                old_is_verified=instance.is_verified,
                new_is_verified=validated_data.get('is_verified'),
                old_expend_date=instance.expend_date,
                new_expend_date=validated_data.get('expend_date'),
                old_uuid=instance.uuid,
                is_updated=True,
                is_deleted=False,
                is_restored=False,
                description=validated_data.get('extra_description'),
            )
            instance.expend_heading = validated_data.get('expend_heading', instance.expend_heading)
            instance.expend_by = validated_data.get('expend_by', instance.expend_by)
            instance.description = validated_data.get('description', instance.description)
            instance.amount = validated_data.get('amount', instance.amount)
            instance.expend_date = validated_data.get('expend_date', instance.expend_date)
            instance.is_verified = validated_data.get('is_verified', instance.is_verified)

            instance.save()

            return instance
        raw_amount = instance.amount
        new_amount = validated_data.get('amount', instance.amount)
        test_amount = new_amount - raw_amount

        expend_obj_non_ref = self.base_user_model().all_expenditure_records.all().filter(
            is_for_refund=False,
            is_deleted=False)
        expend_obj_ref = self.base_user_model().all_expenditure_records.all().filter(
            is_for_refund=True,
            is_deleted=False)
        credit_fund_obj = self.base_user_model().credit_funds.filter(is_deleted=False)

        all_credit_fund_amounts = [obj.amount for obj in credit_fund_obj]
        all_record_amounts_ref = [obj.amount for obj in expend_obj_ref]
        all_record_amounts_non_ref = [obj.amount for obj in expend_obj_non_ref]

        total_pre_credit_fund_amount = utils.sum_int_of_array(all_credit_fund_amounts)
        total_pre_record_amount_non_ref = utils.sum_int_of_array(all_record_amounts_non_ref)
        total_pre_record_amount_ref = utils.sum_int_of_array(all_record_amounts_ref)

        final_value_after_edit = total_pre_record_amount_non_ref + test_amount

        real_asset = (total_pre_credit_fund_amount - total_pre_record_amount_ref)

        if real_asset >= final_value_after_edit:
            # Todo: add history with is_updated = True
            expend_models.ExpenditureRecordHistoryModel.objects.create(
                action_by=self.logged_in_user(),
                base_user=self.base_user_model(),
                related_records=instance,
                old_expend_heading=instance.expend_heading,
                new_expend_heading=validated_data.get('expend_heading'),
                old_expend_by=instance.expend_by,
                new_expend_by=validated_data.get('expend_by'),
                old_description=instance.description,
                new_description=validated_data.get('description'),
                old_amount=instance.amount,
                new_amount=validated_data.get('amount'),
                old_is_verified=instance.is_verified,
                new_is_verified=validated_data.get('is_verified'),
                old_expend_date=instance.expend_date,
                new_expend_date=validated_data.get('expend_date'),
                old_uuid=instance.uuid,
                is_updated=True,
                is_deleted=False,
                is_restored=False,
                description=validated_data.get('extra_description'),
            )
            instance.expend_heading = validated_data.get('expend_heading', instance.expend_heading)
            instance.expend_by = validated_data.get('expend_by', instance.expend_by)
            instance.description = validated_data.get('description', instance.description)
            instance.amount = validated_data.get('amount', instance.amount)
            instance.expend_date = validated_data.get('expend_date', instance.expend_date)
            instance.is_verified = validated_data.get('is_verified', instance.is_verified)

            instance.save()

            return instance
        raise serializers.ValidationError(detail='Credit Fund will be exceede! So you cannot add any more records. After authority add more Credit Fund in Database you can entry more records.')




