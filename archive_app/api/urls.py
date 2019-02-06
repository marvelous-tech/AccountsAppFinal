from django.urls import path
from archive_app.api import views

app_name = "archive-app"

urlpatterns = [
    path('credit/archives/', views.CreditFundArchiveAPIView.as_view(), name="credit_archive"),
    path('expenditure/archives/', views.ExpenditureRecordArchiveAPIView.as_view(), name="expenditure_archive"),
]
