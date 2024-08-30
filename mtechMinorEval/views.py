from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def home(request):
    return render(request,'mtechMinorEval/home.html')

def projectsList(request):
    return render(request,'mtechMinorEval/projectsList.html')