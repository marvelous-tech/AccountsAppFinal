from rest_framework import serializers
from expenditure.models import (
    ExpenditureHeadingModel,
    ExpenditureHeadingHistoryModel,
    ExpenditureRecordHistoryModel,
    ExpenditureRecordModel
)
from base_user.models import BaseUserModel
from sub_user.models import SubUserModel
from utils import utils
import uuid


class ExpenditureHeadingModelSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='expenditure_app:heading_view_update',
        lookup_field='uuid'
    )
    extra_description = serializers.CharField(max_length=255, read_only=False, write_only=True, allow_blank=True)

    class Meta:
        model = ExpenditureHeadingModel
        exclude = ('base_user', )
        read_only_fields = ('uuid', 'added', 'updated')

    def request_data(self):
        return self.context['request']

    def logged_in_user(self):
        return self.request_data().user

    def base_user_model(self):
        base_user = BaseUserModel.objects.filter(base_user=self.logged_in_user())
        sub_user = SubUserModel.objects.filter(root_user=self.logged_in_user())

        if base_user.exists():
            return self.logged_in_user().base_user
        if sub_user.exists():
            return self.logged_in_user().root_sub_user.base_user

    def create(self, validated_data):
        validated_data.pop('extra_description')
        obj = ExpenditureHeadingModel.objects.create(
            base_user=self.logged_in_user().base_user,
            uuid=uuid.uuid4(),
            **validated_data
        )

        return obj

    def update(self, instance, validated_data):
        is_deleted = validated_data.get('is_deleted')

        if is_deleted is True and instance.is_deleted is False:
            if self.base_user_model().all_expenditure_records.filter(expend_heading=instance, is_deleted=False).exists():
                raise serializers.ValidationError(detail="You have one or more debit records which belong to this debit head.", code=400)
            instance.is_deleted = True
            history = ExpenditureHeadingHistoryModel
            history.objects.create(
                related_heading=instance,
                action_by=self.logged_in_user(),
                base_user=self.base_user_model(),
                old_heading_name=instance.heading_name,
                new_heading_name=validated_data.get('heading_name'),
                old_description=instance.description,
                new_description=validated_data.get('description'),
                old_uuid=instance.uuid,
                is_updated=False,
                is_deleted=True,
                is_restored=False,
                description=validated_data.get('extra_description')
            )
            instance.save()
            return instance

        if instance.is_deleted is True and validated_data.get('is_deleted') is False:
            history = ExpenditureHeadingHistoryModel
            history.objects.create(
                related_heading=instance,
                action_by=self.logged_in_user(),
                base_user=self.base_user_model(),
                old_heading_name=instance.heading_name,
                new_heading_name=validated_data.get('heading_name'),
                old_description=instance.description,
                new_description=validated_data.get('description'),
                old_uuid=instance.uuid,
                is_updated=False,
                is_deleted=False,
                is_restored=True,
                description=validated_data.get('extra_description')
            )
            instance.is_deleted = False
            instance.save()
            return instance

        history = ExpenditureHeadingHistoryModel
        history.objects.create(
            related_heading=instance,
            action_by=self.logged_in_user(),
            base_user=self.base_user_model(),
            old_heading_name=instance.heading_name,
            new_heading_name=validated_data.get('heading_name'),
            old_description=instance.description,
            new_description=validated_data.get('description'),
            old_uuid=instance.uuid,
            is_updated=True,
            is_deleted=False,
            is_restored=False,
            description=validated_data.get('extra_description')
        )

        instance.heading_name = validated_data.get('heading_name', instance.heading_name)
        instance.description = validated_data.get('description', instance.description)

        instance.save()

        return instance


class ExpenditureRecordModelSafeSerializer(serializers.ModelSerializer):
    edit_url = serializers.HyperlinkedIdentityField(
        view_name='expenditure_app:record_view_update',
        lookup_field='uuid'
    )

    details_url = serializers.HyperlinkedIdentityField(
        view_name='expenditure_app:record_view',
        lookup_field='uuid'
    )

    expend_heading_name = serializers.SerializerMethodField()
    added_by = serializers.SerializerMethodField()
    extra_description = serializers.CharField(max_length=255, read_only=False, write_only=True, allow_blank=True)

    class Meta:
        model = ExpenditureRecordModel
        exclude = ('base_user', )
        read_only_fields = ('uuid', 'added_by', 'added', 'updated', 'is_verified', 'is_for_refund', 'is_for_return', 'is_verified_once')

    def request_data(self):
        return self.context['request']

    def logged_in_user(self):
        return self.request_data().user

    def base_user_model(self):
        base_user = BaseUserModel.objects.filter(base_user=self.logged_in_user())
        sub_user = SubUserModel.objects.filter(root_user=self.logged_in_user())

        if base_user.exists():
            return self.logged_in_user().base_user
        if sub_user.exists():
            return self.logged_in_user().root_sub_user.base_user

    def create(self, validated_data):
        new_value = validated_data.get('amount')

        expend_obj = self.base_user_model().all_expenditure_records.all().filter(is_deleted=False)
        credit_obj = self.base_user_model().credit_funds.filter(is_deleted=False)

        all_credit_amounts = [obj.amount for obj in credit_obj]
        all_expend_amounts = [obj.amount for obj in expend_obj]

        total_pre_credit_amount = utils.sum_int_of_array(all_credit_amounts)
        total_pre_expend_amount = utils.sum_int_of_array(all_expend_amounts)

        full_balance = total_pre_credit_amount - (total_pre_expend_amount + new_value)

        if full_balance >= 0:
            obj = ExpenditureRecordModel.objects.create(
                added_by=self.logged_in_user(),
                base_user=self.base_user_model(),
                uuid=uuid.uuid4(),
                **validated_data
            )
            return obj
        raise serializers.ValidationError(detail='Credit Fund will be exceed! So you cannot add any more records. After authority add more Credit Fund in Database you can entry more records.')

    def update(self, instance, validated_data):

        if instance.is_verified is False and instance.is_verified_once is False and validated_data.get('is_verified') is True:
            instance.is_verified_once = True
            instance.is_verified = validated_data.get('is_verified', instance.is_verified)
            instance.save()
            return instance

        # Todo: this will wrap in else block
        if instance.is_deleted is False and validated_data.get('is_deleted') is True:
            instance.is_deleted = True
            # Todo: add history with is_deleted = True
            ExpenditureRecordHistoryModel.objects.create(
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

            expend_obj = self.base_user_model().all_expenditure_records.all().filter(is_deleted=False)
            credit_obj = self.base_user_model().credit_funds.filter(is_deleted=False)

            all_credit_amounts = [obj.amount for obj in credit_obj]
            all_expend_amounts = [obj.amount for obj in expend_obj]

            total_pre_credit_amount = utils.sum_int_of_array(all_credit_amounts)
            total_pre_expend_amount = utils.sum_int_of_array(all_expend_amounts)

            full_balance = total_pre_credit_amount - (total_pre_expend_amount + raw_amount)

            if full_balance >= 0:
                instance.is_deleted = False
                ExpenditureRecordHistoryModel.objects.create(
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

        raw_amount = instance.amount
        new_amount = validated_data.get('amount', instance.amount)



        expend_obj = self.base_user_model().all_expenditure_records.all().filter(is_deleted=False)
        credit_obj = self.base_user_model().credit_funds.filter(is_deleted=False)

        all_credit_amounts = [obj.amount for obj in credit_obj]
        all_expend_amounts = [obj.amount for obj in expend_obj]

        total_pre_credit_amount = utils.sum_int_of_array(all_credit_amounts)
        total_pre_expend_amount = utils.sum_int_of_array(all_expend_amounts)

        full_balance = total_pre_credit_amount - (total_pre_expend_amount - raw_amount + new_amount)

        if full_balance >= 0:
            # Todo: add history with is_updated = True
            ExpenditureRecordHistoryModel.objects.create(
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

    @staticmethod
    def get_expend_heading_name(obj):
        return obj.expend_heading.__str__()
    
    @staticmethod
    def get_added_by(obj):
        return obj.added_by.__str__()


class ExpenditureRecordModelSerializer(ExpenditureRecordModelSafeSerializer):

    class Meta:
        model = ExpenditureRecordModel
        exclude = ('base_user', )
        read_only_fields = ('uuid', 'added_by', 'added', 'updated', 'is_for_refund', 'is_for_return', 'is_verified_once')


class ExpenditureRecordModelForCreateSerializer(ExpenditureRecordModelSafeSerializer):
    extra_description = None

    class Meta:
        model = ExpenditureRecordModel
        exclude = ('base_user', )
        read_only_fields = ('uuid', 'added_by', 'added', 'updated', 'is_for_refund', 'is_for_return', 'is_verified_once')


class ExpenditureRecordVerifyModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExpenditureRecordModel
        fields = ('is_verified', )
        read_only_fields = ('is_verified', 'is_verified_once')

    def create(self, validated_data):
        return None

    def update(self, instance, validated_data):
        instance.is_verified = True
        instance.is_verified_once = True
        instance.save()

        return instance


class ExpenditureRecordForGivinLoanModelSafeSerializer(ExpenditureRecordModelSerializer):
        edit_url = serializers.HyperlinkedIdentityField(
            view_name='expenditure_app:loan_giving_view_update_delete',
            lookup_field='uuid'
        )

        details_url = serializers.HyperlinkedIdentityField(
            view_name='expenditure_app:loan_giving_view',
            lookup_field='uuid'
        )

        def create(self, validated_data):
            new_value = validated_data.get('amount')

            # General Operation

            expend_obj = self.base_user_model().all_expenditure_records.all().filter(is_deleted=False)
            credit_obj = self.base_user_model().credit_funds.filter(is_deleted=False)

            all_credit_amounts = [obj.amount for obj in credit_obj]
            all_expend_amounts = [obj.amount for obj in expend_obj]

            total_pre_credit_amount = utils.sum_int_of_array(all_credit_amounts)
            total_pre_expend_amount = utils.sum_int_of_array(all_expend_amounts)

            full_balance = total_pre_credit_amount - (total_pre_expend_amount + new_value)

            if full_balance >= 0:
                obj = ExpenditureRecordModel.objects.create(
                    added_by=self.logged_in_user(),
                    base_user=self.base_user_model(),
                    uuid=uuid.uuid4(),
                    is_for_return=True,
                    **validated_data
                )
                return obj
            raise serializers.ValidationError(detail='Add: Credit Fund will be exceed! So you cannot add any more records. After authority add more Credit Fund in Database you can entry more records.')

        def update(self, instance, validated_data):

            if instance.is_verified is False and instance.is_verified_once is False and validated_data.get('is_verified') is True:
                instance.is_verified_once = True
                instance.is_verified = validated_data.get('is_verified', instance.is_verified)
                instance.save()
                return instance

            # Todo: this will wrap in else block
            if instance.is_deleted is False and validated_data.get('is_deleted') is True:

                expend_obj_ret = self.base_user_model().all_expenditure_records.all().filter(
                    is_deleted=False,
                    is_for_return=True,
                    is_for_refund=False,
                    )
                credit_obj_ret = self.base_user_model().credit_funds.filter(
                    is_deleted=False,
                    is_returnable=True,
                    is_refundable=False,
                    )

                all_credit_amounts_ret = [obj.amount for obj in credit_obj_ret]
                all_expend_amounts_ret = [obj.amount for obj in expend_obj_ret]

                total_pre_credit_amount_ret = utils.sum_int_of_array(all_credit_amounts_ret)
                total_pre_expend_amount_ret = utils.sum_int_of_array(all_expend_amounts_ret)

                balance_after_delete = total_pre_expend_amount_ret - total_pre_credit_amount_ret - instance.amount
                if balance_after_delete >= 0:
                    instance.is_deleted = True
                    # Todo: add history with is_deleted = True
                    ExpenditureRecordHistoryModel.objects.create(
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
                else:
                    raise serializers.ValidationError("Delete: Retrurn cash will be higher than given loan.")
            if instance.is_deleted is True and validated_data.get('is_deleted') is False:
                # Todo: add history with is_restore = True
                raw_amount = instance.amount

                expend_obj = self.base_user_model().all_expenditure_records.all().filter(is_deleted=False)
                credit_obj = self.base_user_model().credit_funds.filter(is_deleted=False)

                all_credit_amounts = [obj.amount for obj in credit_obj]
                all_expend_amounts = [obj.amount for obj in expend_obj]

                total_pre_credit_amount = utils.sum_int_of_array(all_credit_amounts)
                total_pre_expend_amount = utils.sum_int_of_array(all_expend_amounts)

                full_balance = total_pre_credit_amount - (total_pre_expend_amount + raw_amount)

                if full_balance >= 0:
                    instance.is_deleted = False
                    ExpenditureRecordHistoryModel.objects.create(
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
                    detail='Restore: Credit Fund will be exceede! So you cannot add any more records. After authority add more Credit Fund in Database you can entry more records.')

            raw_amount = instance.amount
            new_amount = validated_data.get('amount', instance.amount)

            expend_obj_ret = self.base_user_model().all_expenditure_records.all().filter(
                is_deleted=False,
                is_for_return=True,
                is_for_refund=False
                )
            credit_obj_ret = self.base_user_model().credit_funds.filter(
                is_deleted=False,
                is_returnable=True,
                is_refundable=False
                )

            all_credit_amounts_ret = [obj.amount for obj in credit_obj_ret]
            all_expend_amounts_ret = [obj.amount for obj in expend_obj_ret]

            total_pre_credit_amount_ret = utils.sum_int_of_array(all_credit_amounts_ret)
            total_pre_expend_amount_ret = utils.sum_int_of_array(all_expend_amounts_ret)

            ret_balance = (total_pre_expend_amount_ret - raw_amount + new_amount) - total_pre_credit_amount_ret

            expend_obj = self.base_user_model().all_expenditure_records.all().filter(is_deleted=False)
            credit_obj = self.base_user_model().credit_funds.filter(is_deleted=False)

            all_credit_amounts = [obj.amount for obj in credit_obj]
            all_expend_amounts = [obj.amount for obj in expend_obj]

            total_pre_credit_amount = utils.sum_int_of_array(all_credit_amounts)
            total_pre_expend_amount = utils.sum_int_of_array(all_expend_amounts)

            full_balance = total_pre_credit_amount - (total_pre_expend_amount - raw_amount + new_amount)
            print(full_balance, ret_balance)

            if full_balance >= 0 and ret_balance >=0:
                # Todo: add history with is_updated = True
                ExpenditureRecordHistoryModel.objects.create(
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
            raise serializers.ValidationError(detail='Update: Credit Fund will be exceede! So you cannot add any more records. After authority add more Credit Fund in Database you can entry more records.')

        @staticmethod
        def get_expend_heading_name(obj):
            return obj.expend_heading.__str__()
        
        @staticmethod
        def get_added_by(obj):
            return obj.added_by.__str__()


class ExpenditureRecordForCreateForGivinLoanModelSafeSerializer(ExpenditureRecordForGivinLoanModelSafeSerializer):
    extra_description = None

    class Meta:
        model = ExpenditureRecordModel
        exclude = ('base_user', )
        read_only_fields = ('uuid', 'added_by', 'added', 'updated', 'is_for_refund', 'is_for_return', 'is_verified_once')


class ExpenditureHeadingsHistoryModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExpenditureHeadingHistoryModel
        fields = '__all__'

    def create(self, validated_data):
        raise serializers.ValidationError("Cannot be added by human.")

    def update(self, instance, validated_data):
        raise serializers.ValidationError("Cannot be updated by human.")


class ExpenditureRecordHistoryModelSerializer(serializers.ModelSerializer):
    action_by = serializers.SerializerMethodField()
    related_records = serializers.SerializerMethodField()
    old_expend_heading = serializers.SerializerMethodField()
    new_expend_heading = serializers.SerializerMethodField()
    is_for_refund = serializers.SerializerMethodField()

    class Meta:
        model = ExpenditureRecordHistoryModel
        fields = '__all__'

    def create(self, validated_data):
        raise serializers.ValidationError("Cannot be added by human.")

    def update(self, instance, validated_data):
        raise serializers.ValidationError("Cannot be updated by human.")

    @staticmethod
    def get_action_by(obj):
        return obj.__str__()

    @staticmethod
    def get_related_records(obj):
        return obj.get_related_records()

    @staticmethod
    def get_old_expend_heading(obj):
        return obj.get_old_expend_heading()

    @staticmethod
    def get_new_expend_heading(obj):
        return obj.get_new_expend_heading()

    @staticmethod
    def get_is_for_refund(obj):
        return obj.get_is_for_refund()
