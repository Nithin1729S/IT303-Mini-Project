from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from users.models import Profile

def loginUser(request):
    if request.user.is_authenticated:
        return redirect('projectsList')
    
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']

        try:
            user=User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request,"Username does not exist")

        user=authenticate(request,username=username,password=password)
        if user is not None:
            try:
                profile = Profile.objects.get(user=user)
                if profile.role == 'faculty':
                    login(request, user)
                    return redirect('projectsList')
                else:
                    messages.error(request, "You do not have permission to access this area")
            except Profile.DoesNotExist:
                messages.error(request, "Profile not found for the user")
        else:
            messages.error(request, "Username or password is incorrect")

    return render(request,'users/login.html')

def logoutUser(request):
    username = request.user.username if request.user.is_authenticated else 'User'
    logout(request)
    messages.error(request,f"{username} was successfully logged out ")
    return redirect('login')