from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.db import IntegrityError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Student, Faculty
from django.contrib import messages
from django import forms
from users.models import Profile
import random
from django.core.mail import send_mail
from django.utils.crypto import get_random_string

class ExtendedUserCreationForm(UserCreationForm):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('faculty', 'Faculty'),
    )
    email = forms.EmailField(required=True) 
    role = forms.CharField(widget=forms.HiddenInput(), initial='faculty')  
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2'] 

    def save(self, commit=True):
        user = super(ExtendedUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']  
        if commit:
            user.save()
        return user


def register(request):
    if request.method == 'POST':
        form = ExtendedUserCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            
            # Check if email already exists in the User model
            if User.objects.filter(email=email).exists():
                messages.error(request, 'This email is already registered. Please try logging in.')
                return render(request, 'users/register.html', {'form': form})
            
            try:
                user = form.save()
                role = 'faculty'
                username = form.cleaned_data.get('username')
                profile = Profile.objects.create(user=user, email=email, role=role)
                Faculty.objects.create(profile=profile, email=email, name=username)

                messages.success(request, 'Account created successfully!')
                return redirect('login')
            
            except IntegrityError as e:
                messages.error(request, 'An unexpected error occurred. Please try again.')

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    if field == 'username' and 'already exists' in error.lower():
                        messages.error(request, 'This username is already taken. Please choose another one.')
                    elif field == 'email' and 'already exists' in error.lower():
                        messages.error(request, 'This email is already registered. Please try logging in.')
                    else:
                        messages.error(request, f"{field}: {error}") 

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


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        print(f"Received email: {email}") 
        print(Faculty.objects.filter(email=email))
        if Faculty.objects.filter(email=email).exists():
            print(Faculty.objects.filter(email=email))
            otp = get_random_string(length=6, allowed_chars='0123456789')
            try:
                send_mail(
                    'Your OTP for Password Reset',
                    f'Your OTP is {otp}',
                    'from@example.com',
                    [email],
                    fail_silently=False,
                )
                request.session['otp'] = otp
                request.session['email'] = email
                messages.success(request, 'An OTP has been sent to your email.')
                return redirect('reset-password', otp=otp)
            except Exception as e:
                 print(f"Error sending email: {e}")  
                 messages.error(request, 'Failed to send OTP. Please try again.')
        else:
            messages.error(request, 'Email not registered as faculty.')

    return render(request, 'users/forgot_password.html')


def reset_password(request, otp):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        new_password = request.POST.get('new_password')

        # Verify OTP
        if entered_otp == request.session.get('otp'):
            email = request.session.get('email')
            try:
                faculty = Faculty.objects.get(email=email)
                user = faculty.profile.user  
                user.set_password(new_password) 
                user.save()
                
                messages.success(request, 'Your password has been updated successfully!')
                return redirect('login') 
            except Faculty.DoesNotExist:
                messages.error(request, 'Faculty not found.')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, 'users/reset_password.html', {'otp': otp})
