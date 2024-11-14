import os
from dotenv import load_dotenv
from django.shortcuts import  redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from mtechMinorEval.models import Profile, Faculty, Project
from users.models import *
from mtechMinorEval.models import *


load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CLIENT_SECRET_FILE = 'mtechMinorEval/static/client.json'

@login_required(login_url='login')
def export_faculty_project_to_google_sheet(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'You need to be logged in to export projects.'}, status=403)
    try:
        creds = None
        token_path = 'token.json'
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        service = build('sheets', 'v4', credentials=creds)
        sheet_data = [['Project Name', 'Student Rollno', 'Student Name', 'Student Email', 'Role']]
        profile = request.user.Profile
        projects = Project.objects.filter(guide__profile=profile) | Project.objects.filter(examiner__profile=profile)
        for project in projects:
            role_label = "Guide" if project.guide.profile == profile else "Examiner"
            sheet_data.append([
                project.title,
                project.student.rollno,
                project.student.name,
                project.student.email,
                role_label,
            ])
        body = {
            'properties': {'title': 'Project Data'},
            'sheets': [{
                'data': [{
                    'rowData': [{'values': [{'userEnteredValue': {'stringValue': str(cell)}} for cell in row]} for row in sheet_data]
                }]
            }]
        }

        spreadsheet = service.spreadsheets().create(body=body).execute()
        sheet_id = spreadsheet.get('spreadsheetId')
        return redirect(f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit")

    except HttpError as err:
        print(f"An error occurred: {err}")
        return JsonResponse({'error': 'Failed to export data to Google Sheets'}, status=500)
    

@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)    
def export_total_eval_to_google_sheet(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'You need to be logged in to export projects.'}, status=403)
    try:
        creds = None
        token_path = 'token.json'
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        service = build('sheets', 'v4', credentials=creds)
        sheet_data = [['Rollno', 'Student Name', 'Project Name', 'Guide Name', 'Examiner Name','Guide Marks','Examiner Marks','Total Marks','S/N']]
        projects = ProjectEvalSummary.objects.all()
        for project in projects:
            sheet_data.append([
                project.student.rollno,
                project.student.name,
                project.project.title,
                project.guide.name,
                project.examiner.name,
                project.guide_score,
                project.examiner_score,
                project.total_score,
                project.sn,
            ])
        body = {
            'properties': {'title': 'MTech IT Minor Project Evaluation'},
            'sheets': [{
                'data': [{
                    'rowData': [{'values': [{'userEnteredValue': {'stringValue': str(cell)}} for cell in row]} for row in sheet_data]
                }]
            }]
        }

        spreadsheet = service.spreadsheets().create(body=body).execute()
        sheet_id = spreadsheet.get('spreadsheetId')
        ActivityLog.objects.create(activity=f"Admin dowloaded total evaluation sheet")
        return redirect(f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit")

    except HttpError as err:
        print(f"An error occurred: {err}")
        return JsonResponse({'error': 'Failed to export data to Google Sheets'}, status=500)
    

    

@login_required(login_url='login')
def export_faculty_eval_to_google_sheet(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'You need to be logged in to export projects.'}, status=403)
    try:
        creds = None
        token_path = 'token.json'
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        service = build('sheets', 'v4', credentials=creds)
        user = request.user
        userEmail = user.email
        userProfile = get_object_or_404(Profile, email=userEmail)
        faculty = get_object_or_404(Faculty, profile=userProfile)
        projects=ProjectEvalSummary.objects.filter(Q(guide=faculty) |
                                                Q(examiner=faculty) )
        sheet_data = [['Rollno', 'Student Name', 'Project Name', 'Role','Marks']]
        for project in projects:
            if project.guide == faculty :
                role='Guide'
                marks=project.guide_score
            else :
                role='Examiner'
                marks=project.examiner_score
            sheet_data.append([
                project.student.rollno,
                project.student.name,
                project.project.title,
                role,
                marks
            ])
        body = {
            'properties': {'title': f"{faculty.name}'s MTech IT Minor Project Evaluation"},
            'sheets': [{
                'data': [{
                    'rowData': [{'values': [{'userEnteredValue': {'stringValue': str(cell)}} for cell in row]} for row in sheet_data]
                }]
            }]
        }
        spreadsheet = service.spreadsheets().create(body=body).execute()
        sheet_id = spreadsheet.get('spreadsheetId')
        ActivityLog.objects.create(activity=f"{faculty.name} dowloaded his evaluation sheet")

        return redirect(f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit")
    except HttpError as err:
        print(f"An error occurred: {err}")
        return JsonResponse({'error': 'Failed to export data to Google Sheets'}, status=500)
    


@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def export_faculty_details_to_google_sheet(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'You need to be logged in to export projects.'}, status=403)
    try:
        creds = None
        token_path = 'token.json'
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        service = build('sheets', 'v4', credentials=creds)
        facultys=Faculty.objects.all()
        sheet_data = [['Faculty Name', 'Email']]
        for faculty in facultys:
            sheet_data.append([
                faculty.name,
                faculty.email
            ])
        body = {
            'properties': {'title': f"Facultys Data"},
            'sheets': [{
                'data': [{
                    'rowData': [{'values': [{'userEnteredValue': {'stringValue': str(cell)}} for cell in row]} for row in sheet_data]
                }]
            }]
        }
        spreadsheet = service.spreadsheets().create(body=body).execute()
        sheet_id = spreadsheet.get('spreadsheetId')
        return redirect(f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit")
    except HttpError as err:
        print(f"An error occurred: {err}")
        return JsonResponse({'error': 'Failed to export data to Google Sheets'}, status=500)
    


@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def export_student_details_to_google_sheet(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'You need to be logged in to export projects.'}, status=403)
    try:
        creds = None
        token_path = 'token.json'
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        service = build('sheets', 'v4', credentials=creds)
        students=Student.objects.all()
        sheet_data = [['Student Rollno','Student Name', 'Email','CGPA']]
        for student in students:
            sheet_data.append([
                student.rollno,
                student.name,
                student.email,
                student.cgpa
            ])
        body = {
            'properties': {'title': f"Students' Data"},
            'sheets': [{
                'data': [{
                    'rowData': [{'values': [{'userEnteredValue': {'stringValue': str(cell)}} for cell in row]} for row in sheet_data]
                }]
            }]
        }
        spreadsheet = service.spreadsheets().create(body=body).execute()
        sheet_id = spreadsheet.get('spreadsheetId')
        return redirect(f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit")
    except HttpError as err:
        print(f"An error occurred: {err}")
        return JsonResponse({'error': 'Failed to export data to Google Sheets'}, status=500)


@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def export_project_details_to_google_sheet(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'You need to be logged in to export projects.'}, status=403)
    try:
        creds = None
        token_path = 'token.json'
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        service = build('sheets', 'v4', credentials=creds)
        projects=Project.objects.all()
        sheet_data = [['Project Title','Student Rollno', 'Student Name','Guide','Examiner']]
        for project in projects:
            sheet_data.append([
                project.title,
                project.student.rollno,
                project.student.name,
                project.guide,
                project.examiner
            ])
        body = {
            'properties': {'title': f"Projects' Data"},
            'sheets': [{
                'data': [{
                    'rowData': [{'values': [{'userEnteredValue': {'stringValue': str(cell)}} for cell in row]} for row in sheet_data]
                }]
            }]
        }
        spreadsheet = service.spreadsheets().create(body=body).execute()
        sheet_id = spreadsheet.get('spreadsheetId')
        return redirect(f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit")
    except HttpError as err:
        print(f"An error occurred: {err}")
        return JsonResponse({'error': 'Failed to export data to Google Sheets'}, status=500)
    
