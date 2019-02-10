from rest_framework import serializers
from company.models import CompanyInfoModel
import uuid


class CompanyInfoModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = CompanyInfoModel
        fields = (
            'name',
            'title',
            'address',
            'company_type',
            'created'
            )
    
    def request_data(self):
        return self.context['request']
    
    def logged_in_user(self):
        return self.request_data().user

    def create(self, validated_data):
        obj = CompanyInfoModel.objects.create(
            **validated_data,
            base_user=self.logged_in_user().base_user,
            uuid=uuid.uuid4(),
            is_approved=False
            )
        
        return obj
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.title = validated_data.get('title', instance.title)
        instance.address = validated_data.get('address', instance.address)
        instance.company_type = validated_data.get('company_type', instance.company_type)
        instance.created = validated_data.get('created', instance.created)

        instance.save()

        return instance
