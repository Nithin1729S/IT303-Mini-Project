from django.urls import path
from . import views
urlpatterns=[
    path('',views.projectsList,name='home'),
    path('projectsList/',views.projectsList,name='projectsList'),
    path('evaluate/<str:pk>/',views.evaluate,name='evaluate'),
    path('summary/',views.summary,name='summary'),
    path('totalEval/',views.totalEval,name='total-eval'),
    path('generate-pdf/',views.generate_pdf,name='generate-pdf'),
    path('admin-panel/',views.adminPanel,name='admin-panel'),
    path('admin-login/',views.adminLogin,name='admin-login'),
    path('admin-logout/', views.adminLogout, name='admin-logout'),
    path('project-allotment/', views.projectAllotment, name='project-allotment'),
    path('student-database/', views.studentDatabase, name='student-database'),
    path('faculty-database/', views.facultyDatabase, name='faculty-database'),
    path('project-edit/<str:pk>', views.editProject, name='project-edit'),
    path('student-edit/<str:pk>', views.editStudent, name='student-edit'),
    path('faculty-edit/<str:pk>', views.editFaculty, name='faculty-edit'),
    path('faculty-delete/<str:pk>', views.deleteFaculty, name='faculty-delete'),
    path('project-delete/<str:pk>', views.deleteProject, name='project-delete'),
    path('student-delete/<str:pk>', views.deleteStudent, name='student-delete'),
    path('add-new-project/',views.addNewProject,name='add-new-project'),
    path('add-new-student/',views.addNewStudent,name='add-new-student'),
    path('add-new-faculty/',views.addNewFaculty,name='add-new-faculty'),
    path('export-faculty-project/', views.export_faculty_project_to_google_sheet, name='faculty-project-export'),
    path('export-total-eval/', views.export_total_eval_to_google_sheet, name='total-eval-export'),
    path('export-faculty-eval/', views.export_faculty_eval_to_google_sheet, name='faculty-eval-export'),
    path('faculty-evals/<str:pk>',views.faculty_specific_eval,name='faculty-specific')
]