from django.urls import path
from .views import logoutUser,loginUser
from . import views
from .views import forgot_password, reset_password,verify_otp
urlpatterns = [
    path('login/',views.loginUser,name='login'),
    path('logout/',views.logoutUser,name='logout'),
    path('register/',views.register,name='register'),
    path('forgot-password/', forgot_password, name='forgot-password'),
    path('reset-password/<str:otp>/', reset_password, name='reset-password'),
    path('verify-otp/', verify_otp, name='verify_otp'),
]
