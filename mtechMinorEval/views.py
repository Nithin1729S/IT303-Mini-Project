from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
# Create your views here.
from .models import *
from .forms import ExaminerEvaluationForm, GuideEvaluationForm
from users.models import *
from weasyprint import HTML, CSS
from django.db.models import Q
from django.template.loader import render_to_string

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
    user = request.user
    userEmail = user.email
    userProfile = get_object_or_404(Profile, email=userEmail)
    faculty = get_object_or_404(Faculty, profile=userProfile)
    projects = Project.objects.select_related('student', 'guide', 'examiner')\
                              .prefetch_related('guide_evaluation', 'examiner_evaluation')\
                              .filter(Q(guide=faculty) | Q(examiner=faculty))
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
    }
    return render(request,'mtechMinorEval/generate-pdf-summary.html', context)