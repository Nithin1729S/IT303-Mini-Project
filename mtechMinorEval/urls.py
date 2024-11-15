from django.urls import path
from . import views
from . import export_sheet_views
from . import edit_entity_views
from . import delete_entity_views
from . import create_entity_views
from users.admin_auth_views import adminLogin,adminLogout

urlpatterns=[
    path('',views.projectsList,name='home'),
    path('projectsList/',views.projectsList,name='projectsList'),
    path('evaluate/<str:pk>/',views.evaluate,name='evaluate'),
    path('summary/',views.summary,name='summary'),
    path('faculty-evals/<str:pk>',views.faculty_specific_eval,name='faculty-specific'),
    path('totalEval/',views.totalEval,name='total-eval'),
    path('generate-pdf/',views.generate_pdf,name='generate-pdf'),
    path('admin-panel/',views.adminPanel,name='admin-panel'),
    path('admin-login/',adminLogin,name='admin-login'),
    path('admin-logout/', adminLogout, name='admin-logout'),
    path('project-allotment/', views.projectAllotment, name='project-allotment'),
    path('student-database/', views.studentDatabase, name='student-database'),
    path('faculty-database/', views.facultyDatabase, name='faculty-database'),
    path('project-edit/<str:pk>', edit_entity_views.editProject, name='project-edit'),
    path('student-edit/<str:pk>', edit_entity_views.editStudent, name='student-edit'),
    path('faculty-edit/<str:pk>', edit_entity_views.editFaculty, name='faculty-edit'),
    path('faculty-delete/<str:pk>', delete_entity_views.deleteFaculty, name='faculty-delete'),
    path('project-delete/<str:pk>', delete_entity_views.deleteProject, name='project-delete'),
    path('student-delete/<str:pk>', delete_entity_views.deleteStudent, name='student-delete'),
    path('add-new-project/',create_entity_views.addNewProject,name='add-new-project'),
    path('add-new-student/',create_entity_views.addNewStudent,name='add-new-student'),
    path('add-new-faculty/',create_entity_views.addNewFaculty,name='add-new-faculty'),
    path('export-faculty/',export_sheet_views.export_faculty_details_to_google_sheet,name='export-faculty'),
    path('export-student/',export_sheet_views.export_student_details_to_google_sheet,name='export-student'),
    path('export-project/',export_sheet_views.export_project_details_to_google_sheet,name='export-project'),
    path('export-faculty-project/', export_sheet_views.export_faculty_project_to_google_sheet, name='faculty-project-export'),
    path('export-total-eval/', export_sheet_views.export_total_eval_to_google_sheet, name='total-eval-export'),
    path('export-faculty-eval/', export_sheet_views.export_faculty_eval_to_google_sheet, name='faculty-eval-export'),
    path('access-counts/', views.access_count_view, name='access-counts'),
    path('send_report/',views.send_evaluation_report_to_faculty,name='send-report'),
    path('activity_log/',views.activity_log,name='activity-log')
]