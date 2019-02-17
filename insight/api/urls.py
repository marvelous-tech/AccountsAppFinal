from django.urls import path
from insight.api.views import InsightCreditDebitYearListAPIView


urlpatterns = [
    path('yearly/', InsightCreditDebitYearListAPIView.as_view()),
]
