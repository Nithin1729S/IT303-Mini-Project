import os
import requests
from dotenv import load_dotenv
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from users.notifications_views import send_login_email
from .tasks import log_activity
load_dotenv()


def adminLogin(request):
    "Function to allow module adminstrator to log in"
    if request.method == 'POST':
        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': os.getenv('RECAPTCHA_SECRET_KEY'),  
            'response': recaptcha_response
        }
        try:
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)

            if r.status_code != 200:
                messages.error(request, 'Failed to verify reCAPTCHA. Please try again.')
                return redirect('admin-login')

            result = r.json()

            if not result.get('success'):
                messages.error(request, 'Invalid reCAPTCHA. Please try again.')
                return redirect('admin-login')

        except requests.exceptions.RequestException as e:
            messages.error(request, f"reCAPTCHA verification failed: {str(e)}")
            return redirect('login')
        
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_superuser:
                login(request, user)
                recipient_list = [user.email]
                send_login_email(user.username,recipient_list)
                messages.success(request, "Admin successfully logged in")
                log_activity.delay(f'Admin logged in')
                return redirect('admin-panel') 
            else:
                messages.error(request, "You are not an admin of this module")
                return redirect('login')  
        else:
            messages.error(request, "You don't have an account in this module. Register !")
            return redirect('register')

    return render(request, 'mtechMinorEval/adminLogin.html',{'site_key':os.getenv('RECAPTCHA_SITE_KEY')})


@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser)
def adminLogout(request):
    "Admin logout"
    logout(request)  # This logs out the user
    messages.success(request, "Admin successfully logged out")
    log_activity.delay(f'Admin logged out')
    return redirect('admin-login')  # Redirect to the login page after logout

