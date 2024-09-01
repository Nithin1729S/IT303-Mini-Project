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
def evaluate(request,pk):
    project=Project.objects.get(id=pk)
    print(project)
    user=request.user
    userEmail = user.email
    userProfile = get_object_or_404(Profile, email=userEmail)
    faculty = get_object_or_404(Faculty, profile=userProfile)
    role=""
    if project.guide == faculty:
        form=ExaminerEvaluationForm()
        role='Guide'
    elif project.examiner == faculty:
        form=GuideEvaluationForm()
        role='Examiner'
    else:
        return HttpResponse("You are not authorized to access this resource")
    context={'form':form,'role':role}
    return render(request,'mtechMinorEval/projectEvaluation.html',context=context)