from django.db import models
from django.contrib.auth.models import User
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.validators import RegexValidator

class Profile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
    ('faculty', 'Faculty'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True,blank=True,related_name='Profile')
    email=models.EmailField(max_length=200,unique=True,null=True,blank=True)
    id = models.UUIDField(default=uuid.uuid4,unique=True,primary_key=True,editable=False)
    created=models.DateTimeField(auto_now_add=True,null=True,blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


class Student(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('NB', 'Non-binary'),
        ('O', 'Other'),
        ('PNS', 'Prefer not to say'),
    ]
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, limit_choices_to={'role': 'student'},related_name='Student')
    name=models.CharField(max_length=255,null=True,blank=True)
    profile_image=models.ImageField(upload_to='pics',default='student.svg')
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,  
        blank=True,     
        null=True       
    )
    email=models.EmailField(max_length=200,unique=True,null=True,blank=True)
    rollno=models.CharField(max_length=200,unique=True,null=True,blank=True)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2,null=True,blank=True,validators=[
        MinValueValidator(0.0),
        MaxValueValidator(10.0)
    ])
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(max_length=200,blank=True, null=True)
    fathersName=models.TextField(max_length=200,null=True,blank=True)
    gender = models.CharField(
        max_length=3,
        choices=GENDER_CHOICES,
        default='PNS',
        blank=True,
        null=True
    )
    degree=models.CharField(max_length=200,null=True,blank=True)
    aadhaar_number=models.CharField(max_length=200,null=True,blank=True)
    mother_tongue=models.CharField(max_length=200,null=True,blank=True)
    parents_phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,  
        blank=True,     
        null=True       
    )
    nationality=models.CharField(max_length=200,null=True,blank=True)
    pincode_regex = RegexValidator(
        regex=r'^\d{6}$',
        message="Pincode must be a 6-digit number."
    )
    pincode = models.CharField(
        validators=[pincode_regex],
        max_length=6,
        blank=True,
        null=True
    )
    country=models.CharField(max_length=200,null=True,blank=True)
    branch=models.CharField(max_length=200,null=True,blank=True)
    date_of_admission=models.DateField(null=True,blank=True)
        
    def __str__(self):
        return f"{self.name}"

class Faculty(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('NB', 'Non-binary'),
        ('O', 'Other'),
        ('PNS', 'Prefer not to say'),
    ]
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, limit_choices_to={'role': 'faculty'},related_name='Faculty')
    name=models.CharField(max_length=255,null=True,blank=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,  
        blank=True,     
        null=True       
    )
    email=models.EmailField(max_length=200,unique=True,null=True,blank=True)
    facultyID=models.CharField(max_length=200,unique=True,null=True,blank=True)
    profile_image=models.ImageField(upload_to='pics',default='faculty.svg')
    gender = models.CharField(
        max_length=3,
        choices=GENDER_CHOICES,
        default='PNS',
        blank=True,
        null=True
    )
    nationality=models.CharField(max_length=200,null=True,blank=True)
    country=models.CharField(max_length=200,null=True,blank=True)
    def __str__(self):
        return f"{self.name}"
