import os
import pytz
import random
import socket
import platform
import threading
import datetime
from datetime import datetime
from dotenv import load_dotenv
from django.core.mail import send_mail
from twilio.rest import Client


load_dotenv()

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
    email_thread = threading.Thread(target=send_mail, args=(subject, message, from_email, recipient_list))
    email_thread.start()    
    print(message)
    

def send_faculty_otp(subject,message,recipient_list):
    "Send otp to faculty"
    from_email = os.getenv('MAIL')  
    print(message)
    send_mail(subject, message, from_email, recipient_list,fail_silently=False)

def send_sms(message,to):
    print(message)
    account_sid=os.getenv('TWILIO_SID')
    auth_token=os.getenv('TWILIO_AUTHTOKEN')
    client = Client(account_sid, auth_token)
    message = client.messages.create(
    #messaging_service_sid='MG2f6a62ceae5ed730c7fa15a9ad623446',
    messaging_service_sid = os.getenv('TWILIO_MESSAGE_SERVICE_SID'),
    body=message,
    to=to
    )