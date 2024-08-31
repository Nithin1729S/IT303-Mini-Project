from django.db import models
from django.contrib.auth.models import User
import uuid

class Profile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
    ('faculty', 'Faculty'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True,blank=True)
    id = models.UUIDField(default=uuid.uuid4,unique=True,primary_key=True,editable=False)
    created=models.DateTimeField(auto_now_add=True,null=True,blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


class Student(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    name=models.CharField(max_length=255,null=True,blank=True)
    rollno=models.CharField(max_length=200,null=True,blank=True)
    def __str__(self):
        return f"{self.name}"

class Faculty(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, limit_choices_to={'role': 'faculty'})
    name=models.CharField(max_length=255,null=True,blank=True)
    facultyID=models.CharField(max_length=200,null=True,blank=True)
    def __str__(self):
        return f"{self.name}"
