from django.urls import path, include
from expenditure.api import views

app_name = 'expenditure_app'

urlpatterns = [
    path('heading/', include([
        path('list/', views.ExpenditureHeadingListAPIView.as_view(), name="heading_list"),
        path('list-add/', views.ExpenditureHeadingListCreateAPIView.as_view(), name='heading_list_add'),
        path('view-update-delete/<uuid:uuid>/',
            views.ExpenditureHeadingRetrieveUpdateAPIView.as_view(), name='heading_view_update'),
        path('history/', views.ExpenditureHeadingHistory.as_view(), name="heading_history")
    ])),
    path('record/', include([
        path('list/', views.ExpenditureRecordListAPIView.as_view(), name='record_list'),
        path('add/', views.ExpenditureRecordCreateAPIView.as_view(), name='record_list_add'),
        path('view/<uuid:uuid>/',
            views.ExpenditureRecordRetrieveAPIView.as_view(), name='record_view'),
        path('view-update-delete/<uuid:uuid>/',
            views.ExpenditureRecordRetrieveUpdateAPIView.as_view(), name='record_view_update'),
        path('loan-giving/', include([
            path('list/', views.ExpenditureRecordForGivingLoanListAPIView.as_view(), name='loan_giving_lis_'),
            path('add/', views.ExpenditureRecordForGivingLoanCreateAPIView.as_view(), name='loan_giving_add'),
            path('view/<uuid:uuid>/', views.ExpenditureRecordForGivingLoanRetrieveAPIView.as_view(), name='loan_giving_view'),
            path('view-update-delete/<uuid:uuid>/', views.ExpenditureRecordForGivingLoanRetrieveUpdateAPIView.as_view(), name='loan_giving_view_update_delete')
        ])),
        path('history/', views.ExpenditureRecordHistory.as_view(), name="record_history"),
        path('checkout-today/', views.ExpenditureCheckoutToday.as_view(), name='checkout_today')
    ])),
    path('records-mail-csv/', views.ExpenditureRecordEmailCSV.as_view(), name='records_mail_csv'),
    path('records-report-pdf/', views.ExpenditureRenderPDF.as_view(), name='records_report_pdf')
]
