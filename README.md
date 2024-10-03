# IT303 Software Engineering MTech IT Minor Project Marks Submission Module

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

7. Start the development server:
   ```
   python manage.py runserver
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
```

Make sure to replace the placeholders with your actual credentials.

## Google Sheets API Credentials

Create a JSON file containing your Google Sheets API credentials and save it in the `mtechMinorEval/static` directory with the name `client.json` . This file is necessary for the application to interact with Google Sheets.

## Running the Application

After completing the setup and configuration steps, you can access the application by opening a web browser and navigating to the address provided by the development server (typically http://127.0.0.1:8000/).