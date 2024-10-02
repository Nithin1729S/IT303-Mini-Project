from django.forms import ModelForm
from django.forms.widgets import NumberInput
from django import forms
from django.contrib.auth.models import User
from .models import ExaminerEvaluation,GuideEvaluation,Project,Student,Faculty,Profile
from django.core.exceptions import ValidationError

class ExaminerEvaluationForm(ModelForm):
    class Meta:
        model=ExaminerEvaluation
        exclude=[]
        fields=['datetime_from','datetime_to','depthOfUnderstanding','workDoneAndResults','exceptionalWork','vivaVoce','presentation','report','comments']
        widgets={
            'datetime_from': forms.DateTimeInput(
                attrs={
                    'class': 'form-control', 
                    'id': 'datetime_from',
                    'type':'datetime-local'
                }
            ),
            'datetime_to': forms.DateTimeInput(
                attrs={
                    'class': 'form-control', 
                    'id': 'datetime_to',
                    'type':'datetime-local'
                }
            ),
            'depthOfUnderstanding':forms.NumberInput(
                attrs={
                    'min':0,
                    'max':8,
                    'class': 'form-control', 
                    'id': 'depthOfUnderstanding',
                }
            ),
            'workDoneAndResults':forms.NumberInput(
                attrs={
                    'min':0,
                    'max':12,
                    'class': 'form-control', 
                    'id': 'workDoneAndResults',
                }
            ),
            'exceptionalWork':forms.NumberInput(
                attrs={
                    'min':0,
                    'max':6,
                    'class': 'form-control', 
                    'id': 'exceptionalWork',
                }
            ),
            'vivaVoce':forms.NumberInput(
                attrs={
                    'min':0,
                    'max':8,
                    'class': 'form-control', 
                    'id': 'vivaVoce',
                }
            ),
            'presentation':forms.NumberInput(
                attrs={
                    'min':0,
                    'max':4,
                    'class': 'form-control', 
                    'id': 'presentation',
                }
            ),
            'report':forms.NumberInput(
                attrs={
                    'min':0,
                    'max':2,
                    'class': 'form-control', 
                    'id': 'report',
                }
            ),
            'comments':forms.TextInput(
                attrs={
                    'class':'form-control',
                    'id':'comments'
                }
            ),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            
            for field in self.fields:
                self.fields[field].initial = getattr(instance, field)
       
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.instance.pk is None:  
            instance.project = self.initial['project']
            instance.examiner = self.initial['examiner']
        if commit:
            instance.save()
        return instance

class GuideEvaluationForm(ModelForm):
    class Meta:
        model=GuideEvaluation
        exclude=[]
        fields=['datetime_from','datetime_to','depthOfUnderstanding','workDoneAndResults','exceptionalWork','vivaVoce','presentation','report','attendance','comments']
        widgets={
            'datetime_from': forms.DateTimeInput(
                attrs={
                        'class': 'form-control', 
                        'id': 'datetime_from',
                        'type':'datetime-local'
                       }
            ),
            'datetime_to': forms.DateTimeInput(
                attrs={
                        'class': 'form-control', 
                        'id': 'datetime_to',
                        'type':'datetime-local'
                       }
            ),
            'depthOfUnderstanding':forms.NumberInput(
                attrs={
                    'min':0,
                    'max':12,
                    'class': 'form-control', 
                    'id': 'depthOfUnderstanding',
                }
            ),
            'workDoneAndResults':forms.NumberInput(
                attrs={
                    'min':0,
                    'max':18,
                    'class': 'form-control', 
                    'id': 'workDoneAndResults',
                }
            ),
            'exceptionalWork':forms.NumberInput(
                attrs={
                    'min':0,
                    'max':6,
                    'class': 'form-control', 
                    'id': 'exceptionalWork',
                }
            ),
            'vivaVoce':forms.NumberInput(
                attrs={
                    'min':0,
                    'max':12,
                    'class': 'form-control', 
                    'id': 'vivaVoce'
                }
            ),
            'presentation':forms.NumberInput(
                attrs={
                    'min':0,
                    'max':6,
                    'class': 'form-control', 
                    'id': 'presentation',
                }
            ),
            'report':forms.NumberInput(
                attrs={
                    'min':0,
                    'max':3,
                    'class': 'form-control', 
                    'id': 'report',
                }
            ),
            'attendance':forms.NumberInput(
                attrs={
                    'min':0,
                    'max':3,
                    'class': 'form-control', 
                    'id': 'attendance',
                }
            ),
            'comments':forms.TextInput(
                attrs={
                    'class':'form-control',
                    'id':'comments'
                }
            ),
            
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            for field in self.fields:
                self.fields[field].initial = getattr(instance, field)
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.instance.pk is None:  
            instance.project = self.initial['project']
            instance.guide = self.initial['guide']
        if commit:
            instance.save()
        return instance
    
class ProjectEditForm(ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'desc', 'src_link', 'student', 'examiner', 'guide', 'deadline']
        widgets = {
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        examiner = cleaned_data.get("examiner")
        guide = cleaned_data.get("guide")

        # Ensure the examiner and guide are different
        if examiner == guide:
            raise forms.ValidationError("The examiner and guide must be different.")
        return cleaned_data

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['email']  # This allows editing the email in Profile


class StudentEditForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'id': 'password',
            'placeholder': 'Enter your password',
            'autocomplete':"new-password",
        }), 
        required=False
    )
    class Meta:
        model = Student
        fields = ['name', 'email', 'rollno','cgpa','profile_image','phone_number','date_of_birth','address','fathersName','degree','aadhaar_number','mother_tongue','parents_phone_number','nationality','country','branch','date_of_admission','gender','pincode']
        widgets={
            'cgpa':forms.NumberInput(
                attrs={
                    'min':0.0,
                    'max':10.0,
                    'class': 'form-control', 
                    'id': 'cgpa',
                    'placeholder': 'Enter your CGPA',
                }
            ),
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'id': 'name',
                'placeholder': 'Enter your name',
                'required': 'true'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'id': 'email',
                'placeholder': 'Enter your email',
                'required': 'true'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'id': 'phone_number',
                'placeholder': '+91 1234567890',
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select mb-0', 
                'id': 'gender',
                'aria-label': 'Gender select example'
            }),
            'nationality': forms.TextInput(attrs={
                'class': 'form-control', 
                'id': 'nationality',
                'placeholder': 'Enter your nationality',
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control', 
                'id': 'country',
                'placeholder': 'Enter your country',
            }),
            'degree': forms.TextInput(attrs={
                'class': 'form-control', 
                'id': 'degree',
                'placeholder': 'Enter your Degree',
            }),
            'fathersName': forms.TextInput(attrs={
                'class': 'form-control', 
                'id': 'fathersName',
                'placeholder': 'Enter your Fathers Name',
            }),
            'mother_tongue': forms.TextInput(attrs={
                'class': 'form-control', 
                'id': 'mother_tongue',
                'placeholder': 'Enter your mother tongue',
            }),
            'aadhaar_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'id': 'aadhaar_number',
                'placeholder': 'Enter your Aadhaar number',
            }),
            'branch': forms.TextInput(attrs={
                'class': 'form-control', 
                'id': 'branch',
                'placeholder': 'Enter your branch',
            }),
            'date_of_admission': forms.TextInput(attrs={
                 'class': 'form-control', 
                'id': 'date_of_admission',
                'placeholder': 'dd/mm/yy',
                'data-datepicker':''
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control', 
                'id': 'address',
                'placeholder': 'Enter your address',
            }),
            'rollno': forms.TextInput(attrs={
                'class': 'form-control', 
                'id': 'rollno',
                'placeholder': 'Enter your Roll number',
            }),
            'pincode': forms.TextInput(attrs={
                'class': 'form-control', 
                'id': 'pincode',
                'placeholder': 'Enter your Pincode',
            }),
            'password': forms.TextInput(attrs={
                'class': 'form-control', 
                'id': 'password',
                'placeholder': '********',
            }),
            'date_of_birth': forms.TextInput(attrs={
                'class': 'form-control', 
                'id': 'date_of_birth',
                'placeholder': 'dd/mm/yy',
                'data-datepicker':''
            }),
            'profile_image': forms.FileInput(attrs={
                'class': 'form-control-file',
                'id': 'profile_image'
            }),
        }

    def __init__(self, *args, **kwargs):
        student = kwargs.get('instance')
        super(StudentEditForm, self).__init__(*args, **kwargs)

        if student and student.profile and student.profile.user:
            # Populate password field with an empty value
            self.fields['password'].initial = ''

    def save(self, commit=True):
        student = super(StudentEditForm, self).save(commit=False)
        user = student.profile.user
        # Set the username to the student's name
        user.username = student.name  
        password = self.cleaned_data['password']
        if password:
            user.set_password(password)

        if commit:
            user.save()
            student.save()
        return student

    def clean_email(self):
        email = self.cleaned_data.get('email')
        student_instance = self.instance
        if student_instance.pk and student_instance.profile and student_instance.profile.user:
            if User.objects.filter(email=email).exclude(id=student_instance.profile.user.id).exists():
                raise forms.ValidationError('This email is already in use.')
        else:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError('This email is already in use.')
        return email


class FacultyEditForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'id': 'password',
            'placeholder': 'Enter your password',
        }), 
        required=False
    )
    class Meta:
        model = Faculty
        fields = ['name', 'email', 'facultyID','phone_number','profile_image','gender','nationality','country','date_of_birth','address','pincode']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'id': 'name',
                'placeholder': 'Enter your name',
                'required': 'true'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'id': 'email',
                'placeholder': 'Enter your email',
                'required': 'true'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'id': 'phone_number',
                'placeholder': '+91 1234567890',
                'required': 'true'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select mb-0', 
                'id': 'gender',
                'aria-label': 'Gender select example'
            }),
            'nationality': forms.TextInput(attrs={
                'class': 'form-control', 
                'id': 'nationality',
                'placeholder': 'Enter your nationality',
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control', 
                'id': 'country',
                'placeholder': 'Enter your country',
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control', 
                'id': 'address',
                'placeholder': 'Enter your address',
            }),
            'facultyID': forms.TextInput(attrs={
                'class': 'form-control', 
                'id': 'facultyID',
                'placeholder': 'Enter your faculty ID',
            }),
            'pincode': forms.TextInput(attrs={
                'class': 'form-control', 
                'id': 'pincode',
                'placeholder': 'Enter your Pincode',
            }),
            'date_of_birth': forms.TextInput(attrs={
                'class': 'form-control', 
                'id': 'date_of_birth',
                'placeholder': 'dd/mm/yy',
                'data-datepicker':''
            }),
            'profile_image': forms.FileInput(attrs={
                'class': 'form-control-file',
                'id': 'profile_image'
            }),
        }

    def __init__(self, *args, **kwargs):
        faculty = kwargs.get('instance')
        super(FacultyEditForm, self).__init__(*args, **kwargs)

        if faculty and faculty.profile and faculty.profile.user:
            # Populate password field with an empty value
            self.fields['password'].initial = ''

    def save(self, commit=True):
        faculty = super(FacultyEditForm, self).save(commit=False)
        user = faculty.profile.user
        # Set the username to the faculty's name
        user.username = faculty.name  
        password = self.cleaned_data['password']
        if password:
            user.set_password(password)

        if commit:
            user.save()
            faculty.save()
        return faculty

    def clean_email(self):
        email = self.cleaned_data.get('email')
        faculty_instance = self.instance
        if faculty_instance.pk and faculty_instance.profile and faculty_instance.profile.user:
            if User.objects.filter(email=email).exclude(id=faculty_instance.profile.user.id).exists():
                raise forms.ValidationError('This email is already in use.')
        else:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError('This email is already in use.')
        return email

