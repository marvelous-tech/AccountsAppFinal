from rest_framework import serializers
from base_user.models import BaseUserModel
import uuid
from django.contrib.auth import get_user_model
from credit.models import CreditFundSettingsModel
from user.models import UserExtraInfoModel
User = get_user_model()


class BaseUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = BaseUserModel
        fields = '__all__'


class UserModelSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')

    @staticmethod
    def validate_email(value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(detail='That email address is already taken.')
        return value

    def validate(self, attrs):
        password = attrs['password']
        password2 = attrs.pop('password2')
        if password != password2:
            raise serializers.ValidationError(detail='Password must match.')
        return attrs

    def create(self, validated_data):
        password = validated_data.get('password')
        username = validated_data.get('username')
        email = validated_data.get('email')

        obj = User.objects.create_user(username=username, email=email, password=password)
        base_user = BaseUserModel.objects.create(base_user=obj, uuid=uuid.uuid4())
        CreditFundSettingsModel.objects.create(base_user=base_user)

        UserExtraInfoModel.objects.create(user=obj, base_user=True)
        return obj
