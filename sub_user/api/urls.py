from django.urls import path, include
from sub_user.api import views

app_name = 'sub_user'

urlpatterns = [
    path('list/', views.SubUserListAPIView.as_view(), name='list_sub_user'),
    path('add/', views.SubUserCreateAPIView.as_view(), name='add_sub_user'),
    path('edit/<uuid:uuid>/', views.SubUserEditAPIView.as_view(), name='edit_sub_user'),
    path('view/', views.GetSubUserData.as_view())
]
