from rest_framework import serializers
from user.models import UserExtraInfoModel


class UserExtraInfoModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserExtraInfoModel
        fields = '__all__'
