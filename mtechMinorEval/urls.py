from django.urls import path
from mtechMinorEval.admin_views import access_count_view, activity_log, adminPanel, facultyDatabase, projectAllotment, studentDatabase, summary, totalEval
from mtechMinorEval.create_entity_views import addNewFaculty, addNewProject, addNewStudent
from mtechMinorEval.delete_entity_views import deleteFaculty, deleteProject, deleteStudent
from mtechMinorEval.edit_entity_views import editFaculty, editProject, editStudent
from mtechMinorEval.export_sheet_views import export_faculty_details_to_google_sheet, export_faculty_eval_to_google_sheet, export_faculty_project_to_google_sheet, export_project_details_to_google_sheet, export_student_details_to_google_sheet, export_total_eval_to_google_sheet
from mtechMinorEval.faculty_views import evaluate, faculty_specific_eval, generate_pdf, projectsList, send_evaluation_report_to_faculty
from users.admin_auth_views import adminLogin,adminLogout

urlpatterns=[
    path('',projectsList,name='home'),
    path('projectsList/',projectsList,name='projectsList'),
    path('evaluate/<str:pk>/',evaluate,name='evaluate'),
    path('summary/',summary,name='summary'),
    path('faculty-evals/<str:pk>',faculty_specific_eval,name='faculty-specific'),
    path('totalEval/',totalEval,name='total-eval'),
    path('generate-pdf/',generate_pdf,name='generate-pdf'),
    path('admin-panel/',adminPanel,name='admin-panel'),
    path('admin-login/',adminLogin,name='admin-login'),
    path('admin-logout/', adminLogout, name='admin-logout'),
    path('project-allotment/', projectAllotment, name='project-allotment'),
    path('student-database/', studentDatabase, name='student-database'),
    path('faculty-database/', facultyDatabase, name='faculty-database'),
    path('project-edit/<str:pk>', editProject, name='project-edit'),
    path('student-edit/<str:pk>',editStudent, name='student-edit'),
    path('faculty-edit/<str:pk>', editFaculty, name='faculty-edit'),
    path('faculty-delete/<str:pk>', deleteFaculty, name='faculty-delete'),
    path('project-delete/<str:pk>', deleteProject, name='project-delete'),
    path('student-delete/<str:pk>', deleteStudent, name='student-delete'),
    path('add-new-project/',addNewProject,name='add-new-project'),
    path('add-new-student/',addNewStudent,name='add-new-student'),
    path('add-new-faculty/',addNewFaculty,name='add-new-faculty'),
    path('export-faculty/',export_faculty_details_to_google_sheet,name='export-faculty'),
    path('export-student/',export_student_details_to_google_sheet,name='export-student'),
    path('export-project/',export_project_details_to_google_sheet,name='export-project'),
    path('export-faculty-project/', export_faculty_project_to_google_sheet, name='faculty-project-export'),
    path('export-total-eval/', export_total_eval_to_google_sheet, name='total-eval-export'),
    path('export-faculty-eval/', export_faculty_eval_to_google_sheet, name='faculty-eval-export'),
    path('access-counts/', access_count_view, name='access-counts'),
    path('send_report/',send_evaluation_report_to_faculty,name='send-report'),
    path('activity_log/',activity_log,name='activity-log')
]