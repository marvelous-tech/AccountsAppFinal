from rest_framework import generics
from base_user.api.serializers import UserModelSerializer, BaseUserSerializer
from base_user.api.permissions import BaseUserCreatePermission
from project.permissions import OnlyBaseUser


class BaseUserCreateAPIView(generics.CreateAPIView):
    permission_classes = [BaseUserCreatePermission, ]
    serializer_class = UserModelSerializer

    def get_queryset(self):
        return self.request.user


class GetBaseUserData(generics.RetrieveAPIView):
    serializer_class = BaseUserSerializer
    permission_classes = [OnlyBaseUser, ]
    def get_object(self):
        return self.request.user.base_user
