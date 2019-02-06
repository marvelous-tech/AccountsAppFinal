from django.urls import path
from loan_management.api import views as loan_views

app_name = 'loan-app'

urlpatterns = [
    path('credit/list-add/', loan_views.LoanCreditListCreateAPIView.as_view()),
    path('credit/list/', loan_views.LoanCreditListAPIView.as_view()),
    path('expend/list-add/', loan_views.LoanExpenditureListCreateAPIView.as_view()),
    path('expend/list/', loan_views.LoanExpenditureListAPIView.as_view()),
    path('expend/edit/<uuid:uuid>/', loan_views.LoanExpenditureUpdateAPIView.as_view(), name="expend-update"),
    path('credit/edit/<uuid:uuid>/', loan_views.LoanCreditUpdateAPIView.as_view(), name="credit-update"),
]
