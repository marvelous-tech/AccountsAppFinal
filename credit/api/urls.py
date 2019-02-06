from django.urls import path, include
from credit.api import views

app_name = 'credit_app'

urlpatterns = [
    path('source/', include([
        path('list/', views.CreditFundSourceListAPIView.as_view(), name="fund_source_list"),
        path('list-add/', views.CreditFundSourceListCreateAPIView.as_view(), name='fund_source_list_add'),
        path('view-update-delete/<uuid:uuid>/',
             views.CreditFundSourceRetrieveUpdateAPIView.as_view(), name='fund_source_view_update_delete'),
        path('history/', views.CreditFundSourceHistory.as_view(), name='fund_source_history')
    ])),
    path('fund/', include([
        path('list/', views.CreditFundListAPIView.as_view(), name='fund_list'),
        path('list-add/', views.CreditFundListCreateAPIView.as_view(), name='fund_list_add'),
        path('view-update-delete/<uuid:uuid>/',
             views.CreditFundRetrieveUpdateAPIView.as_view(), name='fund_view_update'),
        path('view/<uuid:uuid>/',
             views.CreditFundRetrieveAPIView.as_view(), name='fund_view'),
        path('history/', views.CreditFundHistory.as_view(), name='fund_history'),
        path('mail-csv/', views.CreditFundGenCSVEmail.as_view()),
        path('settings/', views.CreditFundSettingsView.as_view(), name='fund_settings'),
        path('settings/edit/', views.CreditFundSettingsEditView.as_view(), name='fund_settings_edit')
    ])),
    path('fund-source-list-all/', views.CreditFundsAccordingToSourcesListAPIView.as_view(), name='fund_source_list_all'),
    path('fund-source-report/', views.CreditExportPDFReport.as_view())
]
