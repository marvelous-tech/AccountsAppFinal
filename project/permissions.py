from rest_framework.permissions import BasePermission
from base_user.models import BaseUserModel
from sub_user.models import SubUserModel
from credit.models import CreditFundSettingsModel
from user.models import UserExtraInfoModel


def multiply_bool_array(array):
    result = True
    for value in array:
        result = result * value
    if result is 0:
        return False
    return True


class FundIsNotLocked(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if BaseUserModel.objects.filter(base_user=request.user).exists():
                return request.user.base_user.fund_settings.is_not_locked
            if SubUserModel.objects.filter(root_user=request.user).exists():
                return request.user.root_sub_user.base_user.fund_settings.is_not_locked
            return False
        return False


class OnlyBaseUser(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if UserExtraInfoModel.objects.filter(user=request.user).exists() is False:
                return False
            user_info = request.user.user_extra_info
            return BaseUserModel.objects.filter(
                base_user=request.user
            ).exists() and user_info.is_approved and user_info.is_not_locked
        return False


class OnlySubUser(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if UserExtraInfoModel.objects.filter(user=request.user).exists() is False:
                return False
            user_info = request.user.user_extra_info
            if SubUserModel.objects.filter(root_user=request.user).exists():
                sub_user = SubUserModel.objects.get(root_user=request.user)
                base_user_extra_info = sub_user.base_user.base_user.user_extra_info
                return sub_user.is_active and user_info.is_approved and user_info.is_not_locked and sub_user.is_active \
                    and base_user_extra_info.is_not_locked and base_user_extra_info.is_approved
        return False


class BaseUserOrSubUser(BasePermission):
    
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if UserExtraInfoModel.objects.filter(user=request.user).exists() is False:
                return False
            user_info = request.user.user_extra_info
            if BaseUserModel.objects.filter(base_user=request.user).exists():
                return user_info.is_approved and user_info.is_not_locked
            if SubUserModel.objects.filter(root_user=request.user).exists():
                sub_user = SubUserModel.objects.get(root_user=request.user)
                base_user_extra_info = sub_user.base_user.base_user.user_extra_info
                return sub_user.is_active and user_info.is_approved and user_info.is_not_locked \
                    and sub_user.is_active and base_user_extra_info.is_not_locked and base_user_extra_info.is_approved
            return False
        return False


class BaseUserOrSubUserInfoPermission(BasePermission):
    
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if UserExtraInfoModel.objects.filter(user=request.user).exists() is False:
                return False
            user_info = request.user.user_extra_info
            if BaseUserModel.objects.filter(base_user=request.user).exists():
                return user_info.is_not_locked
            if SubUserModel.objects.filter(root_user=request.user).exists():
                sub_user = SubUserModel.objects.get(root_user=request.user)
                base_user_extra_info = sub_user.base_user.base_user.user_extra_info
                return sub_user.is_active and user_info.is_not_locked \
                    and sub_user.is_active and base_user_extra_info.is_not_locked
            return False
        return False


class SubUserCanList(BasePermission):
    attrs = ['canList']

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            user_info = request.user.user_extra_info
            if BaseUserModel.objects.filter(base_user=request.user).exists():
                return user_info.is_approved and user_info.is_not_locked
            if SubUserModel.objects.filter(root_user=request.user).exists():
                sub_user = SubUserModel.objects.get(root_user=request.user)
                base_user_extra_info = sub_user.base_user.base_user.user_extra_info
                perm_bool_value = [sub_user.__getattribute__(attr) for attr in self.attrs]
                return multiply_bool_array(perm_bool_value) and user_info.is_approved and user_info.is_not_locked \
                    and sub_user.is_active and base_user_extra_info.is_not_locked and base_user_extra_info.is_approved
            return False
        return False


class SubUserCanAdd(SubUserCanList):
    attrs = ['canAdd']


class SubUserCanEdit(SubUserCanList):
    attrs = ['canEdit']


class SubUserCanRetrieve(SubUserCanList):
    attrs = ['canRetrieve']


class SubUserFullAccess(SubUserCanList):
    attrs = ['canList', 'canAdd', 'canRetrieve', 'canEdit']
