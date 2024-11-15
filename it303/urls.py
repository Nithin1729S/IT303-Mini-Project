"""
URL configuration for it303 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from users.faculty_auth_views import change_password_view, forgot_password, login_otp, loginUser,register, reset_password, verify_otp,verify_otp_login
from mtechMinorEval.views import student_profile_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('login/', loginUser, name='login'),
    path('register/', register, name='register'),
    path('forgot-password/', forgot_password, name='forgot-password'),
    path('reset-password/<str:otp>/', reset_password, name='reset-password'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('login-otp/', login_otp, name='login_otp'),
    path('verify-otp-login/', verify_otp_login, name='verify_otp_login'),
    path('student-profile/<str:pk>',student_profile_view,name='student-profile'),
    path('change-password/',change_password_view,name='change_password'),
    path('',include('mtechMinorEval.urls'))  #to allow urls from mtechMinorEval be valid
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
