from rest_framework import permissions
from company.models import CompanyInfoModel
from base_user.models import BaseUserModel
from sub_user.models import SubUserModel


class MustHaveACompany(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            base_user = None
            if BaseUserModel.objects.filter(base_user=request.user).exists():
                base_user = request.user.base_user
            elif SubUserModel.objects.filter(root_user=request.user).exists():
                base_user = request.user.root_sub_user.base_user
            
            if CompanyInfoModel.objects.filter(base_user=base_user).exists():
                return True
            return False

