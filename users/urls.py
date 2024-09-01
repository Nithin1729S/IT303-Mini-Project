from django.urls import path
from .views import logoutUser,loginUser
from . import views
urlpatterns = [
    path('login/',views.loginUser,name='login'),
    path('logout/',views.logoutUser,name='logout'),
]
