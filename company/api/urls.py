from django.urls import path, include
from company.api.views import (
    CompanyInfoCreateAPIView,
    CompanyInfoAPIView,
    CompanyInfoEditAPIView
    )

app_name = 'company_app'

urlpatterns = [
    path('', CompanyInfoAPIView.as_view(), name='company'),
    path('add/', CompanyInfoCreateAPIView.as_view(), name='company_add'),
    path('edit/', CompanyInfoEditAPIView.as_view(), name='company_edit')
]