from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
# Create your views here.
from .models import Project
from .forms import ExaminerEvaluationForm, GuideEvaluationForm

def home(request):
    return render(request,'mtechMinorEval/home.html')

@login_required(login_url='login')
def projectsList(request):
    projects=Project.objects.all()
    context={'projects':projects}
    return render(request,'mtechMinorEval/projectsList.html',context=context)

@login_required(login_url='login')
def evaluate(request):
    formExaminer=ExaminerEvaluationForm()
    formGuide=GuideEvaluationForm
    context={'formExaminer':formExaminer ,'formGuide':formGuide}
    return render(request,'mtechMinorEval/projectEvaluation.html',context=context)