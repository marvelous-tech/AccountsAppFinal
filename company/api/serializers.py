from rest_framework import serializers
from company.models import CompanyInfoModel
import uuid


class CompanyInfoModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = CompanyInfoModel
        fields = (
            'base_user',
            'name',
            'title',
            'address',
            'company_type',
            'created'
            )

    def create(self, validated_data):
        obj = CompanyInfoModel.objects.create(
            **validated_data,
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
