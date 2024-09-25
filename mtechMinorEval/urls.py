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
    path('project-allotment/', views.projectAllotment, name='project-allotment'),
    path('project-edit/<str:pk>', views.editProject, name='project-edit'),
    path('student-edit/<str:pk>', views.editStudent, name='student-edit'),
    path('faculty-edit/<str:pk>', views.editFaculty, name='faculty-edit'),
    path('student-database/', views.studentDatabase, name='student-database'),
    path('faculty-database/', views.facultyDatabase, name='faculty-database'),
    path('faculty-delete/<str:pk>', views.deleteFaculty, name='faculty-delete'),
    path('project-delete/<str:pk>', views.deleteProject, name='project-delete'),
    path('student-delete/<str:pk>', views.deleteStudent, name='student-delete'),
]