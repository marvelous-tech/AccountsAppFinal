from rest_framework import serializers
from django.contrib.auth.models import User


class RootUserModelSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(detail='Passwords mut match')
        return attrs
    
    @staticmethod
    def validate_email(value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(detail='That email address is already taken.')
        return value
    
    def create(self, validated_data):
        username = validated_data.get('username')
        password = validated_data.get('password')
        email = validated_data.get('email')

        obj = User.objects.create_user(username=username, password=password, email=email)

        return obj
    
    def update(self, instance, validated_data):
        validated_data.pop('password')
        validated_data.pop('password2')
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)

        instance.save()

        return instance


class SafeRootUserModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email')
