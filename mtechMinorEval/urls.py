from django.urls import path
from . import views
urlpatterns=[
    path('',views.home,name='home'),
    path('projectsList/',views.projectsList,name='projectsList'),
    path('evaluate/<str:pk>/',views.evaluate,name='evaluate')
]