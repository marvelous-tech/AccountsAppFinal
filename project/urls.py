"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework_jwt.views import verify_jwt_token, refresh_jwt_token
from user.api.views import EditUserInfo
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
]

# ALL APS RELATED URLs
urlpatterns += [
    path('', TemplateView.as_view(template_name="index.html")),
    path('api/', include([
        path('base-user/', include('base_user.api.urls', namespace='base_user')),
        path('sub-user/', include('sub_user.api.urls', namespace='sub_user')),
        path('company/', include('company.api.urls', namespace='company_app')),
        path('credit/', include('credit.api.urls', namespace='credit_app')),
        path('expenditure/', include('expenditure.api.urls', namespace='expenditure_app')),
        path('service/', include('service.api.urls')),
        path('user/extra/', include('user.api.urls')),
        path('loan/', include('loan_management.api.urls', namespace="loan-app")),
        path('archive-app/', include('archive_app.api.urls', namespace="archive-app")),
        path('insight/', include('insight.api.urls')),
    ])),
    path('rest-auth/user/edit/', EditUserInfo.as_view(), name="edit_user_info"),
]
# END HERE

# ALl REST_FRAMEWORK URLs
urlpatterns += [
    re_path(r'^rest-auth/', include('rest_auth.urls')),
    re_path(r'^api-token-verify/', verify_jwt_token),
    re_path(r'^api-token-refresh/', refresh_jwt_token),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# END HERE
