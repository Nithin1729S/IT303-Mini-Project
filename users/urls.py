from django.urls import path
from mtechMinorEval.faculty_views import student_profile_view
from users.faculty_auth_views import change_password_view, forgot_password, login_otp, loginUser, logoutUser, register, reset_password,verify_otp,resend_otp, verify_otp_login
urlpatterns = [
    path('login/',loginUser,name='login'),
    path('logout/',logoutUser,name='logout'),
    path('register/',register,name='register'),
    path('forgot-password/', forgot_password, name='forgot-password'),
    path('reset-password/<str:otp>/', reset_password, name='reset-password'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('resend-otp/',resend_otp,name='resend_otp'),
    path('login-otp/', login_otp, name='login_otp'),
    path('verify-otp-login/',verify_otp_login, name='verify_otp_login'),
    path('student-profile/<str:pk>',student_profile_view,name='student-profile'),
    path('change-password/', change_password_view, name='change_password'),
]
