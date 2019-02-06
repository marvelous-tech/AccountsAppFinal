from rest_framework import generics
from sub_user.api.serializers import RootUserModelSerializer, SubUserModelSerializers
from project.permissions import OnlyBaseUser, OnlySubUser


class SubUserCreateAPIView(generics.CreateAPIView):
    permission_classes = [OnlyBaseUser, ]
    serializer_class = RootUserModelSerializer

    def get_queryset(self):
        return self.request.user


class SubUserListAPIView(generics.ListAPIView):
    permission_classes = [OnlyBaseUser, ]
    serializer_class = SubUserModelSerializers

    def get_queryset(self):
        return self.request.user.base_user.sub_users.all()


class SubUserEditAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [OnlyBaseUser, ]
    serializer_class = SubUserModelSerializers
    lookup_field = 'uuid'

    def get_queryset(self):
        return self.request.user.base_user.sub_users


class GetSubUserData(generics.RetrieveAPIView):
    permission_classes = [OnlySubUser, ]
    serializer_class = SubUserModelSerializers

    def get_object(self):
        return self.request.user.base_user.sub_users
