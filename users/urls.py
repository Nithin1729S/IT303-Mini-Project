from django.urls import path
from . import faculty_auth_views
from mtechMinorEval.faculty_views import student_profile_view
from users.faculty_auth_views import forgot_password, reset_password,verify_otp,resend_otp
urlpatterns = [
    path('login/',faculty_auth_views.loginUser,name='login'),
    path('logout/',faculty_auth_views.logoutUser,name='logout'),
    path('register/',faculty_auth_views.register,name='register'),
    path('forgot-password/', forgot_password, name='forgot-password'),
    path('reset-password/<str:otp>/', reset_password, name='reset-password'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('resend-otp/',resend_otp,name='resend_otp'),
    path('login-otp/', faculty_auth_views.login_otp, name='login_otp'),
    path('verify-otp-login/', faculty_auth_views.verify_otp_login, name='verify_otp_login'),
    path('student-profile/<str:pk>',student_profile_view,name='student-profile'),
    path('change-password/', faculty_auth_views.change_password_view, name='change_password'),
]
