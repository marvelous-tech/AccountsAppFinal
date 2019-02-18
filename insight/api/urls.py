from django.urls import path
from insight.api import views


urlpatterns = [
    path('yearly/', views.InsightCreditDebitYearListAPIView.as_view()),
    path('monthly/', views.InsightCreditDebitMonthlyListAPIView.as_view())
]
