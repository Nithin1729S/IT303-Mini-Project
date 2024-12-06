# IT303 Software Engineering MTech IT Minor Project Marks Submission Module
## Screenshots

### Faculty Register Page
![image](https://github.com/user-attachments/assets/4fd1d92f-b0a3-44ff-9f0f-bb2022d75259)

### Faculty Login Page
![image](https://github.com/user-attachments/assets/2460c7a4-21a5-480b-90fa-c55c4cdb7832)

### Faculty Login via OTP
![image](https://github.com/user-attachments/assets/d790fe58-0a73-450c-93af-14dc01815abe)

### Faculty Forget Password
![image](https://github.com/user-attachments/assets/733f642d-8d87-4c94-94cf-1db43b8e1f56)

### Faculty Dashboard 
![image](https://github.com/user-attachments/assets/c13c059f-d8d6-463b-a5d5-ef4ff2bdbe15)

### Faculty Evaluation Panel
![image](https://github.com/user-attachments/assets/bc2d622f-c8a7-4512-9a32-493b2f4bcbe6)

### Faculty Evaluations
![image](https://github.com/user-attachments/assets/1d61dd87-6cde-42b3-95e7-e4321a18f14a)

### Faculty Profile Edit
![image](https://github.com/user-attachments/assets/5570c045-05df-4795-b26f-387a5322dc9b)


### Faculty Change Password
![image](https://github.com/user-attachments/assets/235362b7-a4b3-4f67-bbce-24144c62aff9)

### Faculty Print Report
![image](https://github.com/user-attachments/assets/8f12802b-be1a-4ad2-88a2-7e0a68f61815)

### Admin Login Page
![image](https://github.com/user-attachments/assets/2002a141-a11f-4a6c-be27-7cfa27c6152c)

### Admin Dashboard
![image](https://github.com/user-attachments/assets/5d286e76-8c1f-48a1-9cec-4900bf61124f)

### Admin Faculty List View
![image](https://github.com/user-attachments/assets/6a566c0c-b6a8-4c89-9a2b-584119a4292a)

### Admin Edit Faculty  View
![image](https://github.com/user-attachments/assets/9e5c05f9-510f-436e-bdac-43cbec356e38)

### Admin Student List View
![image](https://github.com/user-attachments/assets/0a9ee7a0-094c-43b0-8b91-dd52f744737f)

### Admin Edit Student View
![image](https://github.com/user-attachments/assets/415e110e-d541-4f72-ae52-abbc634062ac)

### Admin Project List View
![image](https://github.com/user-attachments/assets/1e840fe6-f939-4418-ba36-f94a96d25dc6)

### Admin Edit Project View
![image](https://github.com/user-attachments/assets/123c564b-7e01-4cdb-a5df-4f273bc9ada9)

### Admin All Evaluation View
![image](https://github.com/user-attachments/assets/ba89ad99-7085-4e1f-8621-729c3bd4ee22)

### Activity Log
![image](https://github.com/user-attachments/assets/8acc423a-9cd3-47eb-940b-9425fa10e552)

## Tech Stack

- **Backend**: Django  
- **Frontend**: Bootstrap  
- **Task Queue**: Celery  
- **Caching/Message Broker**: Redis  
- **Application Server**: Gunicorn 

## Features

### Authentication
- Faculty can log in, log out, and reset their password via OTP-based authentication.  
- Password updates are supported.
- **CAPTCHA** has been added to the login and registration forms to enhance security and prevent automated attacks.  

### Profile Management
- Faculty can edit their profile information.  
- Faculty can view student profiles, including details such as CGPA and other academic records.  

### Project Evaluation
- Faculty can evaluate students' marks based on their role (guide or examiner) as assigned during the guide allocation process.  
- Evaluations can be exported to an Excel sheet.  

### Roles and Permissions
- Faculty can be assigned as a **guide** or **examiner** for specific projects, with evaluation privileges tailored to their role.  
- The admin has higher-level access to the module, overseeing and managing all users, projects, and activities.  

### Reports and Notifications
- Marks reports are automatically generated and sent to faculty via email in PDF format.  
- Background tasks, such as notifications and logging, are handled efficiently using **Celery**.  

### Admin Panel
- Admins can view and manage details for all students, faculty members, and projects.  
- An activity log is available for the admin to monitor all actions performed in the system.

### Performance Enhancements
- **Caching**: Implemented using **Redis** to improve response times for frequently accessed data.  
- **Background Tasks**: Notifications and logging tasks are processed asynchronously using **Celery**, ensuring a smooth user experience.  
- **Backend-Side Pagination**: Added to make API endpoints efficient, reducing the load and improving performance for large datasets.  
- **Search and Sort**: Implemented wherever necessary, allowing for quick data retrieval and better usability.  


## Setup Instructions

1. Open a terminal in the main folder of the project.

2. Install virtualenv:

   ```
   sudo apt install virtualenv
   ```

3. Create a virtual environment:

   ```
   virtualenv env
   ```

4. Activate the virtual environment:

   ```
   source env/bin/activate
   ```

5. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

6. Run database migrations:

   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

7. Start Celery Server
   ```
   celery -A it303 worker --loglevel=debug
   ```
8. Start the server:

   ```
   gunicorn --workers 3 it303.wsgi:application
   ```

8. Create a JSON file with your Google Sheets API credentials and save it in the `mtechMinorEval/static` directory.

## Creating a Superuser

To access the admin panel, create a superuser:

```
python manage.py createsuperuser
```

Follow the prompts to set up your superuser account.

## Environment Variables

Create a `.env` file in the home folder of the project and add your credentials according to the `.env.example` file:

```
EMAIL = 'YOUR_EMAIL_ADDRESS'
PASSWD = 'GOOGLE_SMTP_API_PASSWORD'
TWILIO_SID = 'TWILIO_SID_TOKEN'
TWILIO_AUTHTOKEN= 'TWILIO_AUTHTOKEN'
TWILIO_MESSAGE_SERVICE_SID='TWILIO_MESSAGE_SERVICE_SID'
RECAPTCHA_SITE_KEY='SITE_KEY'
RECAPTCHA_SECRET_KEY='SECRET_KEY'
```

Make sure to replace the placeholders with your actual credentials.

## Google Sheets API Credentials

Create a Desktop application in Google Sheet API dashboard. Download a JSON file containing your Google Sheets API credentials and save it in the `mtechMinorEval/static` directory with the name `client.json` . This file is necessary for the application to interact with Google Sheets.

## Twilio

Create a [messaging service](https://console.twilio.com/us1/develop/sms/services) in twilio console. Use that messaging service to [send an sms to personal number](https://console.twilio.com/us1/develop/sms/try-it-out/send-an-sms). Copy all credentials and paste in .env file.

## Running the Application

After completing the setup and configuration steps, you can access the application by opening a web browser and navigating to the address provided by the development server (typically http://127.0.0.1:8000/).
