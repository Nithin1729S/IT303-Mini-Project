from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse,JsonResponse
from django.db import transaction
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required,user_passes_test
from .models import *
from .forms import ExaminerEvaluationForm, GuideEvaluationForm, ProfileEditForm
from google.auth.transport.requests import Request
from users.models import *
import requests
from weasyprint import HTML
from django.db.models import Q
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.template.loader import render_to_string
from .forms import ProjectEditForm,StudentEditForm,FacultyEditForm
from users.views import send_login_email
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CLIENT_SECRET_FILE = 'mtechMinorEval/static/client.json'
from dotenv import load_dotenv
load_dotenv()

def home(request):
    user = request.user
    userEmail = user.email
    userProfile = get_object_or_404(Profile, email=userEmail)
    faculty = get_object_or_404(Faculty, profile=userProfile)
    return render(request,'mtechMinorEval/home.html',{'faculty':faculty})

from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import Profile, Faculty, Project

from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import Profile, Faculty, Project

@login_required(login_url='login')
def projectsList(request):
    user = request.user
    if user.is_superuser:
        return redirect('admin-panel')

    if user.is_authenticated:
        userEmail = user.email
        userProfile = get_object_or_404(Profile, email=userEmail)

        if userProfile.role == 'faculty':
            faculty = get_object_or_404(Faculty, profile=userProfile)

            # Get search and sorting parameters
            search_query = request.GET.get('search', '')
            per_page = request.GET.get('per_page', 5)
            sort_column = request.GET.get('sort', 'title')
            sort_order = request.GET.get('order', 'asc')

            # Basic query without complex lookups
            projects = Project.objects.filter(
                Q(guide=faculty) | Q(examiner=faculty)
            ).distinct()

            # Simple search on title only
            if search_query:
                projects = projects.filter(title__icontains=search_query)

            # Simple sorting
            if sort_order == 'desc':
                projects = projects.order_by(f'-{sort_column}')
            else:
                projects = projects.order_by(sort_column)

            # Handle pagination
            paginator = Paginator(projects, per_page)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            context = {
                'projects': page_obj,
                'faculty': faculty,
                'search_query': search_query,
                'paginator': paginator,
                'per_page': per_page,
                'sort_column': sort_column,
                'sort_order': sort_order,
            }
            return render(request, 'mtechMinorEval/projectsList.html', context)

        else:
            logout(request)
            return redirect('login')
    else:
        return redirect('login')





@login_required(login_url='login')
def evaluate(request, pk):
    "Evaluate takes the faculty to the evaluation form of the respective form and can be run by only logged in users.."
    project = Project.objects.get(id=pk)
    user = request.user
    userEmail = user.email
    userProfile = get_object_or_404(Profile, email=userEmail)
    faculty = get_object_or_404(Faculty, profile=userProfile)
    
    if project.guide == faculty:
        FormClass = GuideEvaluationForm
        role = 'Guide'
        initial_data = {'project': project, 'guide': faculty}
        evaluation_instance = GuideEvaluation.objects.filter(project=project, guide=faculty).first()
    elif project.examiner == faculty:
        FormClass = ExaminerEvaluationForm
        role = 'Examiner'
        initial_data = {'project': project, 'examiner': faculty}
        evaluation_instance = ExaminerEvaluation.objects.filter(project=project, examiner=faculty).first()
    else:
        return HttpResponse("You are not authorized to access this resource")

    if request.method == 'POST':
        if evaluation_instance:
            form = FormClass(request.POST, instance=evaluation_instance, initial=initial_data)
        else:
            form = FormClass(request.POST, initial=initial_data)
        
        if form.is_valid():
            form.save()
            return redirect('projectsList')
        else:
            print("Form is invalid")
    else:
        if evaluation_instance:
            form = FormClass(instance=evaluation_instance, initial=initial_data)
        else:
            form = FormClass(initial=initial_data)

    total_marks = 0
    if evaluation_instance:
        total_marks = (
            getattr(evaluation_instance, 'depthOfUnderstanding', 0) +
            getattr(evaluation_instance, 'workDoneAndResults', 0) +
            getattr(evaluation_instance, 'exceptionalWork', 0) +
            getattr(evaluation_instance, 'vivaVoce', 0) +
            getattr(evaluation_instance, 'presentation', 0) +
            getattr(evaluation_instance, 'report', 0) +
            getattr(evaluation_instance, 'attendance', 0)
        )
    context = {'form': form, 'role': role,'total_marks':total_marks,'project':project,'faculty':faculty}
    return render(request, 'mtechMinorEval/projectEvaluation.html', context=context)


@login_required(login_url='login')
def summary(request):
    "Gives adminstrator the evaluation summary of entire mtech minor it projects and can be run by only logged in users."
    projects = Project.objects.select_related('student', 'guide', 'examiner')\
                              .prefetch_related('guide_evaluation', 'examiner_evaluation')
    context = {
        'projects': projects,
    }
    return render(request, 'mtechMinorEval/summary.html', context)

@login_required(login_url='login')
def totalEval(request):
    search_query = request.GET.get('search', '')
    per_page = request.GET.get('per_page', 5)  
    sort_column = request.GET.get('sort', 'student__rollno')  
    sort_order = request.GET.get('order', 'asc') 
    if sort_order == 'desc':
        order_by = f'-{sort_column}'
    else:
        order_by = sort_column 

    "Gives adminstrator the evaluation summary of entire mtech minor it projects and can be run by only logged in users."
    projects = ProjectEvalSummary.objects.filter(
                              Q(project__title__icontains=search_query) |
                              Q(student__name__icontains=search_query) |
                              Q(student__rollno__icontains=search_query)
    ).order_by(order_by)
    
    paginator = Paginator(projects, per_page)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'projects': page_obj,
        'search_query': search_query,
        'per_page': per_page,
        'sort_column': sort_column,
        'sort_order': sort_order,
    }
    return render(request, 'mtechMinorEval/totalEval.html', context)


@login_required(login_url='login')
def generate_pdf(request):
    "Generates pdf of the evaluation report and can be run by only logged in users."
    user = request.user
    userEmail = user.email
    userProfile = get_object_or_404(Profile, email=userEmail)
    faculty = get_object_or_404(Faculty, profile=userProfile)
    projects = Project.objects.select_related('student', 'guide', 'examiner')\
                              .prefetch_related('guide_evaluation', 'examiner_evaluation')\
                              .filter(Q(guide=faculty) | Q(examiner=faculty))
    guide_projects_count = Project.objects.filter(guide=faculty).count()
    examiner_projects_count = Project.objects.filter(examiner=faculty).count()

    context = {
        'projects': projects,
        'faculty':faculty,
        'guide_count':guide_projects_count,
        'examiner_count':examiner_projects_count
    }
    
    # Check if the user wants to download the PDF
    if 'download' in request.GET:
        html_string = render_to_string('mtechMinorEval/generate-pdf-summary.html', context)
        pdf_file = HTML(string=html_string).write_pdf()

        # Return the PDF as an HTTP response
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="evaluation_summary.pdf"'
        return response
    
    return render(request,'mtechMinorEval/generate-pdf-summary.html', context)



def faculty_specific_eval(request,pk):
    user = request.user
    userEmail = user.email
    userProfile = get_object_or_404(Profile, email=userEmail)
    faculty = get_object_or_404(Faculty, profile=userProfile)
    search_query = request.GET.get('search', '')
    per_page = request.GET.get('per_page', 5)  
    sort_column = request.GET.get('sort', 'student__rollno')  
    sort_order = request.GET.get('order', 'asc')
    if sort_order == 'desc':
        order_by = f'-{sort_column}'
    else:
        order_by = sort_column 
    projects=ProjectEvalSummary.objects.filter(Q(guide=faculty) |
                                                Q(examiner=faculty) )
    projects=projects.filter(Q(project__title__icontains=search_query) |
                                                  Q(student__name__icontains=search_query) |
                                                   Q(student__rollno__icontains=search_query) 
    ).order_by(order_by)
    paginator = Paginator(projects, per_page)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={
        'faculty':faculty,
        'projects':page_obj,
        'search_query': search_query,
        'per_page': per_page,
        'sort_column': sort_column,
        'sort_order': sort_order,
    }
    return render(request,'mtechMinorEval/facultySpecific.html',context)


def adminLogin(request):
    "Function to allow module adminstrator to log in"
    if request.method == 'POST':
        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': '6LeenVEqAAAAAC01Gp9B4M72_8jRXdgFeWjeL8EQ',  
            'response': recaptcha_response
        }
        try:
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)

            if r.status_code != 200:
                messages.error(request, 'Failed to verify reCAPTCHA. Please try again.')
                return redirect('admin-login')

            result = r.json()

            if not result.get('success'):
                messages.error(request, 'Invalid reCAPTCHA. Please try again.')
                return redirect('admin-login')

        except requests.exceptions.RequestException as e:
            messages.error(request, f"reCAPTCHA verification failed: {str(e)}")
            return redirect('login')
        
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_superuser:
                login(request, user)
                recipient_list = [user.email]
                send_login_email(user.username,recipient_list)
                messages.success(request, "Admin successfully logged in")
                return redirect('admin-panel') 
            else:
                messages.error(request, "You are not an admin of this module")
                return redirect('login')  
        else:
            messages.error(request, "You don't have an account in this module. Register !")
            return redirect('register')

    return render(request, 'mtechMinorEval/adminLogin.html')



@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def adminPanel(request):
        "Gives a panel to admin listing all databases to perform CRUD operations on."
        path_accesses = PathAccess.objects.order_by('-access_count')[:8]
        total_visits = sum(access.access_count for access in path_accesses)
        total_bounces = sum(access.bounces for access in path_accesses)
        bounce_rate = (total_bounces / total_visits) * 100 if total_visits > 0 else 0
        projects = Project.objects.all() 
        students = Student.objects.all() 
        facultys = Faculty.objects.all() 
        context={'projects':projects,'students':students,'facultys':facultys,'path_accesses': path_accesses,
            'bounce_rate': bounce_rate,}
        return render(request,'mtechMinorEval/adminPanel.html', context)



@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def adminLogout(request):
    "Admin logout"
    logout(request)  # This logs out the user
    messages.success(request, "Admin successfully logged out")
    return redirect('admin-login')  # Redirect to the login page after logout



@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def projectAllotment(request):
    "View the projects database."
    search_query = request.GET.get('search', '')
    per_page = request.GET.get('per_page', 5)  
    sort_column = request.GET.get('sort', 'title')  
    sort_order = request.GET.get('order', 'asc')  

    if sort_order == 'desc':
        order_by = f'-{sort_column}'
    else:
        order_by = sort_column

   
    projects= Project.objects.filter(
            Q(title__icontains=search_query) |
            Q(desc__icontains=search_query) |
            Q(student__name__icontains=search_query) |
            Q(student__rollno__icontains=search_query) 
        ).order_by(order_by)

    
    paginator = Paginator(projects, per_page)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'projects': page_obj,
        'search_query': search_query,
        'per_page': per_page,
        'sort_column': sort_column,
        'sort_order': sort_order,
    }
    return render(request, 'mtechMinorEval/projectAllotment.html', context)
    


@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def studentDatabase(request):
    "View the student database."
    search_query = request.GET.get('search', '')
    per_page = request.GET.get('per_page', 5)  # Default to 5 entries per page
    sort_column = request.GET.get('sort', 'name')  # Default sort column is 'name'
    sort_order = request.GET.get('order', 'asc')   # Default order is ascending

    if sort_order == 'desc':
        order_by = f'-{sort_column}'
    else:
        order_by = sort_column

    # Filter students based on the search query
   
    students = Student.objects.filter(
            Q(rollno__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query)
    ).order_by(order_by)

    # Pagination
    paginator = Paginator(students, per_page)  # Use the per_page value
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'students': page_obj,
        'search_query': search_query,
        'per_page': per_page,
        'sort_column': sort_column,
        'sort_order': sort_order,
    }
    return render(request, 'mtechMinorEval/studentDatabase.html', context)



@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def facultyDatabase(request):
    search_query = request.GET.get('search', '')
    per_page = request.GET.get('per_page', 5)
    sort_column = request.GET.get('sort', 'name')  # Default sort column is 'name'
    sort_order = request.GET.get('order', 'asc')   # Default order is ascending

    # Determine the order by adding a minus sign for descending order
    if sort_order == 'desc':
        order_by = f'-{sort_column}'
    else:
        order_by = sort_column

    # Filter facultys based on the search query
    facultys = Faculty.objects.filter(
        Q(name__icontains=search_query) |
        Q(email__icontains=search_query)
    ).order_by(order_by)

    # Pagination
    paginator = Paginator(facultys, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'facultys': page_obj,
        'search_query': search_query,
        'per_page': per_page,
        'sort_column': sort_column,
        'sort_order': sort_order,
    }
    return render(request, 'mtechMinorEval/facultyDatabase.html', context)



@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def editProject(request, pk):
    "Edit a particular project details"
    project = get_object_or_404(Project, id=pk) 
    if request.method == 'POST':
        form = ProjectEditForm(request.POST, request.FILES,instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project details updated successfully.')
            return redirect('project-allotment') 
        else:
            messages.error(request, 'There was an error updating the project.')
    else:
        form = ProjectEditForm(instance=project)
    
    context = {
        'project': project,
        'form': form
    }
    return render(request, 'mtechMinorEval/editProject.html', context)


@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def editStudent(request, pk):
    "Edit a paritcular student details"
    student = Student.objects.get(id=pk)
    profile = student.profile 
    form =StudentEditForm(instance=student)
    profile_form = ProfileEditForm(instance=profile) 

    if request.method == 'POST':
        form = StudentEditForm(request.POST, request.FILES,instance=student)
        profile_form = ProfileEditForm(request.POST, instance=profile) 

        if form.is_valid() and profile_form.is_valid(): 
            form.save()     
            profile_instance = profile_form.save(commit=False)  
            user = profile.user  
            user.email = profile_instance.email  
            user.save()  
            profile_instance.save()  
            messages.success(request, 'Student updated successfully!')
            return redirect('student-database')  
        else:
            messages.error(request, 'Please correct the errors below.')

    context = {
        'student': student,
        'form': form,
        'profile_form': profile_form  
    }
    return render(request, 'mtechMinorEval/editStudent.html', context)


@login_required
def editFaculty(request, pk):
    "Edit a particular faculty details"
    if request.user.is_superuser:
        template = "mtechMinorEval/base.html"
    else:
        template = "mtechMinorEval/base_faculty.html"
    faculty = Faculty.objects.get(id=pk)
    profile = faculty.profile 
    form = FacultyEditForm(instance=faculty)
    profile_form = ProfileEditForm(instance=profile) 

    if request.method == 'POST':
        form = FacultyEditForm(request.POST,request.FILES, instance=faculty)
        profile_form = ProfileEditForm(request.POST, instance=profile) 

        if form.is_valid() and profile_form.is_valid(): 
            print(form)
            form.save()     
            profile_instance = profile_form.save(commit=False)  
            user = profile.user  
            user.email = profile_instance.email  
            user.save()  
            profile_instance.save()  

            messages.success(request, 'Faculty updated successfully!')
            if request.user.is_superuser:
                return redirect('faculty-database')  
            else:
                return redirect('projectsList')
        else:
            messages.error(request, 'Please correct the errors below.')

    context = {
        'faculty': faculty,
        'form': form,
        'profile_form': profile_form  
    }
    if request.user.is_superuser: 
        return render(request, 'mtechMinorEval/editFaculty.html', context)
    else:
        return render(request,'mtechMinorEval/facultyEdit.html',context)



@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def deleteProject(request,pk):
    "Delete a particular project"
    project=Project.objects.get(id=pk)
    context={
        'project':project
    }
    if(request.method=='POST'):
        project.delete()
        return redirect('project-allotment')
    return render(request,'mtechMinorEval/delete.html',context)



@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def deleteStudent(request,pk):
    "Delete a particular student"
    student=Student.objects.get(id=pk)
    profile=student.profile
    user=profile.user
    context={
        'student': student
    }
    with transaction.atomic():
        if(request.method=='POST'):
            student.delete()
            profile.delete()
            user.delete()
            return redirect('student-database')
    return render(request,'mtechMinorEval/delete.html',context)



@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def deleteFaculty(request,pk):
    "Delete a particular faculty"
    faculty=Faculty.objects.get(id=pk)
    profile=faculty.profile
    user=profile.user
    context={
        'faculty': faculty
    }
    with transaction.atomic():
        if(request.method=='POST'):
            faculty.delete()
            profile.delete()
            user.delete()
            return redirect('faculty-database')
    return render(request,'mtechMinorEval/delete.html',context)



@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def addNewProject(request):
    "Add new project"
    if request.method == 'POST':
        form = ProjectEditForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('project-allotment')
    else:
        form = ProjectEditForm()

    context = {'form': form}
    return render(request, 'mtechMinorEval/editProject.html', context)
    


@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def addNewStudent(request):
    "Add new Student"
    if request.method == 'POST':
        form = StudentEditForm(request.POST,request.FILES)
        if form.is_valid():
            with transaction.atomic():
                name = form.cleaned_data.get('name')  # Use the name from the form
                email = form.cleaned_data.get('email')
                password = form.cleaned_data.get('password')
                cgpa=form.cleaned_data.get('cgpa')
                gender=form.cleaned_data.get('gender')
                phone_number=form.cleaned_data.get('phone_number')
                nationality=form.cleaned_data.get('nationality')
                country=form.cleaned_data.get('country')
                fathersName=form.cleaned_data.get('fathersName')
                degree=form.cleaned_data.get('degree')
                mother_tongue=form.cleaned_data.get('mother_tongue')
                aadhaar_number=form.cleaned_data.get('aadhaar_number')
                branch=form.cleaned_data.get('branch')
                date_of_birth=form.cleaned_data.get('date_of_birth')
                date_of_admission=form.cleaned_data.get('date_of_admission')
                address=form.cleaned_data.get('address')
                rollno=form.cleaned_data.get('rollno')
                pincode=form.cleaned_data.get('pincode')
                profile_image=form.cleaned_data.get('profile_image')
                # Create the User object
                user = User.objects.create_user(username=name, email=email, password=password)

                # Create the Profile object
                profile = Profile.objects.create(user=user, email=email, role='student')

                # Create the Student object
                student = Student.objects.create(
                    profile=profile,
                    name=name,  # Use the same name for the Student model
                    email=email,
                    rollno=form.cleaned_data.get('rollno'),
                    cgpa=cgpa,
                    gender=gender,
                    phone_number=phone_number,
                    nationality=nationality,
                    country=country,
                    fathersName=fathersName,
                    degree=degree,
                    mother_tongue=mother_tongue,
                    aadhaar_number=aadhaar_number,
                    branch=branch,
                    date_of_birth=date_of_birth,
                    date_of_admission=date_of_admission,
                    address=address,
                    pincode=pincode,
                    profile_image=profile_image
                )
                
                return redirect('student-database')
    else:
        form = StudentEditForm()

    context = {'form': form}
    return render(request, 'mtechMinorEval/addNewStudent.html', context)




@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def addNewFaculty(request):
    "Add new faculty"
    if request.method == 'POST':
        form = FacultyEditForm(request.POST,request.FILES,)
        if form.is_valid():
            with transaction.atomic():
                # Extract fields from the form
                name = form.cleaned_data.get('name')  # Ensure username is included in the form
                email = form.cleaned_data.get('email')
                password = form.cleaned_data.get('password')  # Assuming password is included in the form
                phone_number = form.cleaned_data.get('phone_number')
                gender = form.cleaned_data.get('gender')
                nationality = form.cleaned_data.get('nationality')
                country = form.cleaned_data.get('country')
                address = form.cleaned_data.get('address')
                date_of_birth = form.cleaned_data.get('date_of_birth')
                profile_image = form.cleaned_data.get('profile_image')
                pincode = form.cleaned_data.get('pincode')
                facultyID = form.cleaned_data.get('facultyID')
                # Ensure username is provided
                if not name:
                    raise ValueError("Username must be provided")

                # Create the User object
                user = User.objects.create_user(username=name, email=email, password=password)
                
                # Create the Profile object
                profile = Profile.objects.create(user=user, email=email, role='faculty')

                # Create the Faculty object
                faculty = Faculty.objects.create(
                    profile=profile,
                    name=form.cleaned_data.get('name'),
                    email=email,
                    facultyID=form.cleaned_data.get('facultyID'),
                    phone_number=phone_number,
                    gender=gender,
                    nationality=nationality,
                    country=country,
                    address=address,
                    date_of_birth=date_of_birth,
                    profile_image=profile_image,
                    pincode=pincode,
                )
                
                return redirect('faculty-database')
    else:
        form = FacultyEditForm()

    context = {'form': form}
    return render(request, 'mtechMinorEval/addNewFaculty.html', context)


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
        return redirect(f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit")

    except HttpError as err:
        print(f"An error occurred: {err}")
        return JsonResponse({'error': 'Failed to export data to Google Sheets'}, status=500)
    

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
        return redirect(f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit")
    except HttpError as err:
        print(f"An error occurred: {err}")
        return JsonResponse({'error': 'Failed to export data to Google Sheets'}, status=500)
    

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
    


from django.shortcuts import render
from .models import PathAccess

# views.py
from django.shortcuts import render
from .models import PathAccess

def access_count_view(request):
    path_accesses = PathAccess.objects.all()
    
    total_visits = sum(access.access_count for access in path_accesses)
    total_bounces = sum(access.bounces for access in path_accesses)

    # Calculate bounce rate
    bounce_rate = (total_bounces / total_visits) * 100 if total_visits > 0 else 0

    context = {
        'path_accesses': path_accesses,
        'bounce_rate': bounce_rate,
    }
    return render(request, 'mtechMinorEval/access_count.html', context)
