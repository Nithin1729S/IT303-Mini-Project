from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
# Create your views here.
from .models import *
from .forms import ExaminerEvaluationForm, GuideEvaluationForm
from users.models import *

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
            print(form.errors)
    else:
        if evaluation_instance:
            form = FormClass(instance=evaluation_instance, initial=initial_data)
        else:
            form = FormClass(initial=initial_data)

    context = {'form': form, 'role': role}
    return render(request, 'mtechMinorEval/projectEvaluation.html', context=context)