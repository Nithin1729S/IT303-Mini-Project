import requests

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect,get_object_or_404
from django.db import IntegrityError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Student, Faculty
from django.contrib import messages
from django import forms
from mtechMinorEval.models import Project
from users.models import Profile
import random
from django.utils import timezone
import re,os,socket,platform
import pytz
import threading
from datetime import datetime
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from dotenv import load_dotenv
load_dotenv()

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

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            # Remove spaces from the username
            username = username.replace(" ", "")
            self.cleaned_data['username'] = username  # Update cleaned_data
        return username
    
    def save(self, commit=True):
        user = super(ExtendedUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']  
        if commit:
            user.save()
        return user



def generate_otp():
    """Generate a random 6-digit OTP"""
    return random.randint(100000, 999999)

def send_login_email(to_faculty,recipient_list):
    "Send login email to faculty"
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_address = s.getsockname()[0]
    timezone = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
    from_email = os.getenv("EMAIL") 
    subject = 'Login Notification'
    message = f'Hello {to_faculty},\n\nYou have successfully logged into the module from IP address {ip_address} on { current_time } running on { platform.system()}.'
    # email_thread = threading.Thread(target=send_mail, args=(subject, message, from_email, recipient_list))
    # email_thread.start()    
    print(message)

def send_faculty_otp(subject,message,recipient_list):
    "Send otp to faculty"
    from_email = os.getenv('MAIL')  
    print(message)
    #send_mail(subject, message, from_email, recipient_list,fail_silently=False)

def register(request):
    "Function to register a new faculty"
    if request.method == 'POST':
        form = ExtendedUserCreationForm(request.POST)
        if form.is_valid():
            recaptcha_response = request.POST.get('g-recaptcha-response')
            data = {
                'secret': '6LeenVEqAAAAAC01Gp9B4M72_8jRXdgFeWjeL8EQ',
                'response': recaptcha_response
            }
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data = data)
            result = r.json()

            if not result['success']:
                    message.error(request, 'Invalid reCAPTCHA. Please try again.')
                    return  redirect('register')

            email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')

            # Check if the email is valid
            # if not email.endswith('@nitk.edu.in'):
            #     messages.error(request, 'Email must end with @nitk.edu.in.')
            #     return render(request, 'users/register.html', {'form': form})

            # Check if the email contains any numbers
            # if re.search(r'\d', email):
            #     messages.error(request, 'Email cannot contain numbers.')
            #     return render(request, 'users/register.html', {'form': form})

            # Check if the email is already registered
            if User.objects.filter(email=email).exists():
                messages.error(request, 'This email is already registered. Please try logging in.')
                return render(request, 'users/register.html', {'form': form})

            # Generate OTP and send it via email
            otp = generate_otp()
            request.session['email'] = email
            request.session['otp'] = otp
            request.session['form_data'] = request.POST  # Save form data in session

            subject = 'Email OTP Verification'
            message = f'Your OTP for registration is: {otp}'
            recipient_list = [email]
            #send_faculty_otp(subject,message,recipient_list)
            print(message)
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
    "Function to login a faculty with reCAPTCHA verification"
    
    if request.user.is_superuser:
        return redirect('admin-panel')
    if request.user.is_authenticated:
        return redirect('projectsList')

    if request.method == 'POST':
        # Fetch the reCAPTCHA response from the POST data
        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': '6LeenVEqAAAAAC01Gp9B4M72_8jRXdgFeWjeL8EQ',  # Your reCAPTCHA secret key
            'response': recaptcha_response
        }

        try:
            # Send a request to Google's reCAPTCHA API to verify the response
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)

            # Check if the request was successful
            if r.status_code != 200:
                messages.error(request, 'Failed to verify reCAPTCHA. Please try again.')
                return redirect('login')

            result = r.json()

            # Check if reCAPTCHA verification was successful
            if not result.get('success'):
                messages.error(request, 'Invalid reCAPTCHA. Please try again.')
                return redirect('login')

        except requests.exceptions.RequestException as e:
            # Handle network-related errors
            messages.error(request, f"reCAPTCHA verification failed: {str(e)}")
            return redirect('login')

        # Proceed with the login logic if CAPTCHA was successful
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)

        if user is not None:
            try:
                profile = Profile.objects.get(user=user)
                if profile.role == 'faculty':
                    login(request, user)
                    recipient_list = [email]
                    send_login_email(profile.user.username, recipient_list)
                    messages.success(request, f'{email} logged in successfully!')
                    return redirect('projectsList')
                else:
                    messages.error(request, "You do not have permission to access this area.")
            except Profile.DoesNotExist:
                messages.error(request, "Profile not found for the user.")
        else:
            messages.error(request, "Email or password is incorrect.")

    return render(request, 'users/login.html')

def login_otp(request):
    "Login via otp"
    if request.method == 'POST':
        email = request.POST.get('email')
        otp = generate_otp()

        # Store OTP and email in session for now
        request.session['otp'] = otp
        request.session['email'] = email

        # Send the OTP to the user's email
        subject = 'Your OTP for Login'
        message = f'Your OTP for login is {otp}. It is valid for 5 minutes.'
        recipient_list = [email]
        send_faculty_otp(subject,message,recipient_list)
        messages.success(request, 'OTP sent to your email.')
        return redirect('verify_otp_login')

    return render(request, 'users/login_otp.html')

def verify_otp_login(request):
    "OTP Verification for login via otp"
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')
        email = request.session.get('email')
        
        if entered_otp == str(session_otp):
            try:
                user = User.objects.get(email=email)
                profile = Profile.objects.get(user=user)
                login(request, user,backend='users.backends.EmailBackend')
                recipient_list = [email]
                send_login_email(profile.user.username,recipient_list)
                messages.success(request, 'Logged in successfully with OTP!')
                return redirect('projectsList')
            except User.DoesNotExist:
                messages.error(request, 'No user found with this email.')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, 'users/verify_otp_login.html')



def logoutUser(request):
    "Logout Faculty"
    username = request.user.username if request.user.is_authenticated else 'User'
    logout(request)
    messages.success(request,f"{username} was successfully logged out ")
    return redirect('login')


def forgot_password(request):
    "Forgot password to reset password"
    if request.method == 'POST':
        email = request.POST.get('email')
        print(f"Received email: {email}") 
        print(Faculty.objects.filter(email=email))
        if Faculty.objects.filter(email=email).exists():
            print(Faculty.objects.filter(email=email))
            otp = get_random_string(length=6, allowed_chars='0123456789')
            try:
                subject="Your OTP for Password Reset",
                message=f'Your OTP is {otp}'
                send_faculty_otp(subject,message,[email])
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
    "Reset password after comparing otp"
    
    # Initialize the resend OTP timestamp if it does not exist
    if 'resend_otp_time' not in request.session:
        request.session['resend_otp_time'] = timezone.now().timestamp()

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

    # Check if 10 seconds have passed for OTP resend
    if timezone.now().timestamp() - request.session['resend_otp_time'] >= 10:
        can_resend = True
    else:
        can_resend = False

    return render(request, 'users/reset_password.html', {'otp': otp, 'can_resend': can_resend})



def verify_otp(request):
    "Verification of OTP for account registration "
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

def student_profile_view(request,pk):
    user = request.user
    userEmail = user.email
    userProfile = get_object_or_404(Profile, email=userEmail)
    faculty = get_object_or_404(Faculty, profile=userProfile)
    student=Student.objects.get(id=pk)
    context={
        'student':student,
        'faculty':faculty
    }
    return render(request,'users/student_profile.html',context)


def resend_otp(request):
    "Resend OTP if requested"
    email = request.session.get('email')
    if email:
        otp = get_random_string(length=6, allowed_chars='0123456789')
        subject = "Your OTP for Password Reset"
        message = f'Your OTP is {otp}'
        send_faculty_otp(subject, message, [email])
        request.session['otp'] = otp
        request.session['resend_otp_time'] = timezone.now().timestamp() 
        messages.success(request, 'A new OTP has been sent to your email.')
    else:
        messages.error(request, 'Unable to resend OTP. Please try again.')

    return redirect('reset-password', otp=request.session.get('otp'))