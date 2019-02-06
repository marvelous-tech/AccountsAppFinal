from django.urls import path
from user.api.views import GetUserExtraInfo


urlpatterns = [
    path('view/', GetUserExtraInfo.as_view()),
]