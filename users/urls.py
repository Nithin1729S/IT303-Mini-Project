from django.urls import path
from .views import logoutUser,loginUser
from . import views
from .views import forgot_password, reset_password,verify_otp,student_profile_view
urlpatterns = [
    path('login/',views.loginUser,name='login'),
    path('logout/',views.logoutUser,name='logout'),
    path('register/',views.register,name='register'),
    path('forgot-password/', forgot_password, name='forgot-password'),
    path('reset-password/<str:otp>/', reset_password, name='reset-password'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('login-otp/', views.login_otp, name='login_otp'),
    path('verify-otp-login/', views.verify_otp_login, name='verify_otp_login'),
    path('student-profile/<str:pk>',views.student_profile_view,name='student-profile')
]
