from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.db import transaction
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required,user_passes_test
from .models import *
from .forms import ExaminerEvaluationForm, GuideEvaluationForm
from users.models import *
from weasyprint import HTML, CSS
from django.db.models import Q
from django.template.loader import render_to_string
from .forms import ProjectEditForm,StudentEditForm,FacultyEditForm


def home(request):
    return render(request,'mtechMinorEval/home.html')


@login_required(login_url='login')
def projectsList(request):
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
    context = {'projects': projects}
    return render(request, 'mtechMinorEval/projectsList.html', context=context)


@login_required(login_url='login')
def evaluate(request, pk):
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
            #print(form.errors)
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
    # print(project.student)
    # print(project.student.rollno)
    context = {'form': form, 'role': role,'total_marks':total_marks,'project':project}
    return render(request, 'mtechMinorEval/projectEvaluation.html', context=context)


@login_required(login_url='login')
def summary(request):
    projects = Project.objects.select_related('student', 'guide', 'examiner')\
                              .prefetch_related('guide_evaluation', 'examiner_evaluation')
    context = {
        'projects': projects,
    }
    return render(request, 'mtechMinorEval/summary.html', context)



@login_required(login_url='login')
def generate_pdf(request):
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
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_superuser:
                login(request, user)
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
        projects = Project.objects.all() 
        print(projects)
        context={'projects':projects}
        return render(request,'mtechMinorEval/adminPanel.html', context)



@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def adminLogout(request):
    logout(request)  # This logs out the user
    messages.success(request, "Admin successfully logged out")
    return redirect('admin-login')  # Redirect to the login page after logout



@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def projectAllotment(request):
    projects=Project.objects.all()
    context={
        'projects':projects
    }
    return render(request,'mtechMinorEval/projectAllotment.html', context)



@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def studentDatabase(request):
    students=Student.objects.all()
    context={
        'students':students
    }
    return render(request,'mtechMinorEval/studentDatabase.html', context)



@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def facultyDatabase(request):
    facultys=Faculty.objects.all()
    context={
        'facultys':facultys
    }
    return render(request,'mtechMinorEval/facultyDatabase.html', context)



@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def editProject(request,pk):
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
    student = Student.objects.get(id=pk)
    form = StudentEditForm(instance=student)
    
    if request.method == 'POST':
        form = StudentEditForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student updated successfully!')
            return redirect('student-database') 
        else:
            messages.error(request, 'Please correct the errors below.')
    
    context = {
        'student': student,
        'form': form
    }
    return render(request, 'mtechMinorEval/editStudent.html', context)



@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def editFaculty(request, pk):
    faculty=Faculty.objects.get(id=pk)
    form=FacultyEditForm(instance=faculty)
    
    if request.method == 'POST':
        form = FacultyEditForm(request.POST, instance=faculty)
        if form.is_valid():
            form.save()
            messages.success(request, 'Faculty updated successfully!')
            return redirect('faculty-database')  # Redirect to the appropriate URL after saving
        else:
            messages.error(request, 'Please correct the errors below.')
    
    context = {
        'faculty': faculty,
        'form': form
    }
    return render(request, 'mtechMinorEval/editFaculty.html', context)



@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def deleteProject(request,pk):
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
    if request.method == 'POST':
        form = StudentEditForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                username = form.cleaned_data.get('username')  # assuming username is included in form
                email = form.cleaned_data.get('email')
                password = form.cleaned_data.get('password')  # assuming password is included in form
                user = User.objects.create_user(username=username, email=email, password=password)
                profile = Profile.objects.create(user=user, email=email, role='student')
                student = Student.objects.create(profile=profile, name=form.cleaned_data.get('name'), 
                                                 email=email, rollno=form.cleaned_data.get('rollno'))
                
                return redirect('student-database')
    else:
        form = StudentEditForm()

    context = {'form': form}
    return render(request, 'mtechMinorEval/editStudent.html', context)



@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def addNewFaculty(request):
    if request.method == 'POST':
        form = FacultyEditForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                username = form.cleaned_data.get('username')  # assuming username is included in form
                email = form.cleaned_data.get('email')
                password = form.cleaned_data.get('password')  # assuming password is included in form
                user = User.objects.create_user(username=username, email=email, password=password)
                profile = Profile.objects.create(user=user, email=email, role='faculty')
                faculty = Faculty.objects.create(profile=profile, name=form.cleaned_data.get('name'), 
                                                 email=email, facultyID=form.cleaned_data.get('facultyID'))
                
                return redirect('faculty-database')
    else:
        form = FacultyEditForm()

    context = {'form': form}
    return render(request, 'mtechMinorEval/editFaculty.html', context)
