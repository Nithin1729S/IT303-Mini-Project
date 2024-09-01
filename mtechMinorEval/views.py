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
def evaluate(request):
    formExaminer=ExaminerEvaluationForm()
    formGuide=GuideEvaluationForm()
    context={'formExaminer':formExaminer ,'formGuide':formGuide}
    return render(request,'mtechMinorEval/projectEvaluation.html',context=context)