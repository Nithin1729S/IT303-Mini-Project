from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required,user_passes_test
# Create your views here.
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

@login_required  # Require login for the content page
@user_passes_test(lambda u: u.is_superuser)
def adminPanel(request):
        projects = Project.objects.all() 
        print(projects)
        context={'projects':projects}
        return render(request,'mtechMinorEval/adminPanel.html', context)


def adminLogout(request):
    logout(request)  # This logs out the user
    messages.success(request, "Admin successfully logged out")
    return redirect('admin-login')  # Redirect to the login page after logout

def projectAllotment(request):
    projects=Project.objects.all()
    context={
        'projects':projects
    }
    return render(request,'mtechMinorEval/projectAllotment.html', context)

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

def studentDatabase(request):
    students=Student.objects.all()
    context={
        'students':students
    }
    return render(request,'mtechMinorEval/studentDatabase.html', context)

def facultyDatabase(request):
    facultys=Faculty.objects.all()
    context={
        'facultys':facultys
    }
    return render(request,'mtechMinorEval/facultyDatabase.html', context)

def editStudent(request,pk):
    student=Student.objects.get(id=pk)
    form=StudentEditForm(instance=student)
    context={
        'student':student,
        'form':form
    }
    if request.method == 'POST':
        pass
    return render(request,'mtechMinorEval/editStudent.html', context)

def editFaculty(request,pk):
    faculty=Faculty.objects.get(id=pk)
    form=FacultyEditForm(instance=faculty)
    context={
        'faculty':faculty,
        'form':form
    }
    if request.method == 'POST':
        pass
    return render(request,'mtechMinorEval/editFaculty.html', context)
