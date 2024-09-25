from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Student, Faculty
from django.contrib import messages
from django import forms
from users.models import Profile

# Extended registration form to include email and role selection
class ExtendedUserCreationForm(UserCreationForm):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('faculty', 'Faculty'),
    )
    email = forms.EmailField(required=True)  # Add the email field
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']  # Add email field

    def save(self, commit=True):
        user = super(ExtendedUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']  # Set the email field for the User model
        if commit:
            user.save()
        return user

def register(request):
    if request.method == 'POST':
        form = ExtendedUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            email = form.cleaned_data.get('email')
            role = form.cleaned_data.get('role')
            username= form.cleaned_data.get('username')

            profile = Profile.objects.create(user=user, email=email, role=role)
            if role == 'student':
                Student.objects.create(profile=profile, email=email,name=username)
            elif role == 'faculty':
                Faculty.objects.create(profile=profile, email=email,name=username)

            messages.success(request, 'Account created successfully!')
            return redirect('login')
        else:
            messages.error(request, 'There was an error creating your account.')
    else:
        form = ExtendedUserCreationForm()

    return render(request, 'users/register.html', {'form': form})


def loginUser(request):
    if request.user.is_authenticated:
        return redirect('projectsList')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            try:
                profile = Profile.objects.get(user=user)
                if profile.role == 'faculty':
                    login(request, user)
                    messages.success(request, f'{email} logged in successfully!')
                    return redirect('projectsList')
                else:
                    messages.error(request, "You do not have permission to access this area.")
            except Profile.DoesNotExist:
                messages.error(request, "Profile not found for the user.")
        else:
            messages.error(request, "Email or password is incorrect.")
    return render(request, 'users/login.html')



def logoutUser(request):
    username = request.user.username if request.user.is_authenticated else 'User'
    logout(request)
    messages.success(request,f"{username} was successfully logged out ")
    return redirect('login')

