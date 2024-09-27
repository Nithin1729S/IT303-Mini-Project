from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.db import transaction
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required,user_passes_test
from .models import *
from .forms import ExaminerEvaluationForm, GuideEvaluationForm, ProfileEditForm
from users.models import *
from weasyprint import HTML, CSS
from django.db.models import Q
from django.template.loader import render_to_string
from .forms import ProjectEditForm,StudentEditForm,FacultyEditForm
from users.views import send_login_email
from dotenv import load_dotenv
load_dotenv()

def home(request):
    return render(request,'mtechMinorEval/home.html')

@login_required(login_url='login')
def projectsList(request):
    "Lists the Projects to which the faculty is a guide or a mentor to and can be run by only logged in users."
    user = request.user
    userEmail = user.email
    userProfile = get_object_or_404(Profile, email=userEmail)
    projects = []
    if userProfile.role == 'faculty':
        faculty = get_object_or_404(Faculty, profile=userProfile)
        guide_projects = Project.objects.filter(guide=faculty)
        examiner_projects = Project.objects.filter(examiner=faculty)
        projects = guide_projects.union(examiner_projects)
    else:
        logout(request,user)
    context = {'projects': projects,'faculty':faculty}
    return render(request, 'mtechMinorEval/projectsList.html', context=context)


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
    context = {'form': form, 'role': role,'total_marks':total_marks,'project':project}
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
def generate_pdf(request):
    "Generates pdf of the evaluation report and can be run by only logged in users."
    user = request.user
    userEmail = user.email
    userProfile = get_object_or_404(Profile, email=userEmail)
    faculty = get_object_or_404(Faculty, profile=userProfile)
    projects = Project.objects.select_related('student', 'guide', 'examiner')\
                              .prefetch_related('guide_evaluation', 'examiner_evaluation')\
                              .filter(Q(guide=faculty) | Q(examiner=faculty))
    context = {
        'projects': projects,
        'faculty':faculty
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



def adminLogin(request):
    "Function to allow module adminstrator to log in"
    if request.method == 'POST':
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
        projects = Project.objects.all() 
        print(projects)
        context={'projects':projects}
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
    projects=Project.objects.all()
    context={
        'projects':projects
    }
    return render(request,'mtechMinorEval/projectAllotment.html', context)



@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def studentDatabase(request):
    "View the student database."
    students=Student.objects.all()
    context={
        'students':students
    }
    return render(request,'mtechMinorEval/studentDatabase.html', context)



@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def facultyDatabase(request):
    "View the faculty database"
    facultys=Faculty.objects.all()
    context={
        'facultys':facultys
    }
    return render(request,'mtechMinorEval/facultyDatabase.html', context)



@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def editProject(request,pk):
    "Edit a particular project details"
    project = Project.objects.get(id=pk)
    form=ProjectEditForm(instance=project)
    context={
        'project':project,
        'form':form
    }
    if request.method == 'POST':
        pass
    return render(request,'mtechMinorEval/editProject.html', context)


@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def editStudent(request, pk):
    "Edit a paritcular student details"
    student = Student.objects.get(id=pk)
    profile = student.profile 
    form =StudentEditForm(instance=student)
    profile_form = ProfileEditForm(instance=profile) 

    if request.method == 'POST':
        form = StudentEditForm(request.POST, instance=student)
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
    faculty = Faculty.objects.get(id=pk)
    profile = faculty.profile 
    form = FacultyEditForm(instance=faculty)
    profile_form = ProfileEditForm(instance=profile) 

    if request.method == 'POST':
        form = FacultyEditForm(request.POST, instance=faculty)
        profile_form = ProfileEditForm(request.POST, instance=profile) 

        if form.is_valid() and profile_form.is_valid(): 
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
    return render(request, 'mtechMinorEval/editFaculty.html', context)



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
        form = StudentEditForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                name = form.cleaned_data.get('name')  # Use the name from the form
                email = form.cleaned_data.get('email')
                password = form.cleaned_data.get('password')
                cgpa=form.cleaned_data.get('cgpa')
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
                    cgpa=cgpa
                )
                
                return redirect('student-database')
    else:
        form = StudentEditForm()

    context = {'form': form}
    return render(request, 'mtechMinorEval/editStudent.html', context)




@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def addNewFaculty(request):
    "Add new faculty"
    if request.method == 'POST':
        form = FacultyEditForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Extract fields from the form
                name = form.cleaned_data.get('name')  # Ensure username is included in the form
                email = form.cleaned_data.get('email')
                password = form.cleaned_data.get('password')  # Assuming password is included in the form
                
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
                    facultyID=form.cleaned_data.get('facultyID')
                )
                
                return redirect('faculty-database')
    else:
        form = FacultyEditForm()

    context = {'form': form}
    return render(request, 'mtechMinorEval/editFaculty.html', context)

