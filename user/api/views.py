from rest_framework import generics
from project.permissions import BaseUserOrSubUser
from user.api.serialzers import UserExtraInfoModelSerializer
from project.serializers import SafeRootUserModelSerializer


class GetUserExtraInfo(generics.RetrieveAPIView):

    permission_classes = [BaseUserOrSubUser, ]
    serializer_class = UserExtraInfoModelSerializer

    def get_object(self):
        return self.request.user.user_extra_info


class EditUserInfo(generics.RetrieveUpdateAPIView):

    permission_classes = [BaseUserOrSubUser, ]
    serializer_class = SafeRootUserModelSerializer

    def get_object(self):
        return self.request.user
