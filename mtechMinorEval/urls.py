from django.urls import path
from . import views
urlpatterns=[
    path('',views.home,name='home'),
    path('projectsList/',views.projectsList,name='projectsList'),
    path('evaluate/<str:pk>/',views.evaluate,name='evaluate'),
    path('summary/',views.summary,name='summary'),
    path('generate-pdf/',views.generate_pdf,name='generate-pdf'),
    path('admin-panel/',views.adminPanel,name='admin-panel'),
    path('admin-login/',views.adminLogin,name='admin-login'),
    path('admin-logout/', views.adminLogout, name='admin-logout'),
]