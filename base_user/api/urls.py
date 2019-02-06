from django.urls import path, include
from base_user.api.views import BaseUserCreateAPIView, GetBaseUserData

app_name = 'base_user'

urlpatterns = [
    path('add/', BaseUserCreateAPIView.as_view(), name='create_base_user'),
    path('view/', GetBaseUserData.as_view())
]
