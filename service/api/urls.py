from django.urls import path
from service.api import views


urlpatterns = [
    path('user/', views.GetUserData.as_view()),
    path('total-fund-amount/', views.GetTotalFundAmount.as_view()),
    path('oh-no/', views.MailOnWrongPassword.as_view()),
    path('oh-no-base-user/', views.MailOnNonBaseUser.as_view()),
    path('what-do-you-want/', views.GrabWhatYouWantedAPIView.as_view()),
    path('fash-all/', views.CreditExpenditureHistoryAPIView.as_view())
]
