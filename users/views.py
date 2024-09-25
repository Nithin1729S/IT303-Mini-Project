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
import re,os,socket,platform
from datetime import datetime
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from dotenv import load_dotenv
load_dotenv()
import geocoder


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

def generate_otp():
    """Generate a random 6-digit OTP"""
    return random.randint(100000, 999999)
    

def register(request):
    if request.method == 'POST':
        form = ExtendedUserCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')

            # Check if the email is valid
            if not email.endswith('@nitk.edu.in'):
                messages.error(request, 'Email must end with @nitk.edu.in.')
                return render(request, 'users/register.html', {'form': form})

            # Check if the email contains any numbers
            if re.search(r'\d', email):
                messages.error(request, 'Email cannot contain numbers.')
                return render(request, 'users/register.html', {'form': form})

            # Check if the email is already registered
            if User.objects.filter(email=email).exists():
                messages.error(request, 'This email is already registered. Please try logging in.')
                return render(request, 'users/register.html', {'form': form})

            # Generate OTP and send it via email
            otp = generate_otp()
            request.session['email'] = email
            request.session['otp'] = otp
            request.session['form_data'] = request.POST  # Save form data in session

            # Send OTP email
            subject = 'Email OTP Verification'
            message = f'Your OTP for registration is: {otp}'
            from_email = 'your-email@domain.com'  # Replace with your email
            recipient_list = [email]
            print(message)
            #send_mail(subject, message, from_email, recipient_list)
            messages.info(request, 'OTP sent to your email. Please verify.')

            return redirect('verify_otp')

        else:
            # Handle form validation errors
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
    if request.user.is_superuser:
        return redirect('admin-panel')
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
                    hostname = socket.gethostname()
                    ip_address = socket.gethostbyname(hostname)
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    g=geocoder.ip('me')
                    location=g.latlng
                    subject = 'Login Notification'
                    message = f'Hello {profile.user.username},\n\nYou have successfully logged into the module from IP address {ip_address} on { current_time } running on { platform.system()}.'
                    from_email = os.getenv("EMAIL") 
                    recipient_list = [email]
                    #send_mail(subject, message, from_email, recipient_list)
                    print(message)
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
            print(otp)
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



def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')
        form_data = request.session.get('form_data')

        # Check if OTP matches
        if entered_otp == str(session_otp):
            try:
                form = ExtendedUserCreationForm(form_data)
                if form.is_valid():
                    user = form.save()
                    email = form.cleaned_data.get('email')
                    username = form.cleaned_data.get('username')
                    role = 'faculty'
                    
                    profile = Profile.objects.create(user=user, email=email, role=role)
                    Faculty.objects.create(profile=profile, email=email, name=username)

                    # Clear session data after successful registration
                    del request.session['otp']
                    del request.session['email']
                    del request.session['form_data']

                    messages.success(request, 'Account created successfully!')
                    return redirect('login')
            except IntegrityError:
                messages.error(request, 'An unexpected error occurred. Please try again.')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, 'users/verify_otp.html')