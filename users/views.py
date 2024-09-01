from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages

def loginUser(request):
    if request.user.is_authenticated:
        return redirect('projectsList')
    
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']

        try:
            user=User.objects.get(username=username)
        except:
            messages.error(request,"Username does not exist")

        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('projectsList')
        else:
            messages.error(request,"Username or password is incorrect")

    return render(request,'users/login.html')

def logoutUser(request):
    logout(request)
    messages.error(request,"Username was successfully logged out ")
    return redirect('login')