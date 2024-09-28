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
            
            'datetime_from': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-input'}),
            'datetime_to': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-input'}),
        
            'depthOfUnderstanding':forms.NumberInput(
                attrs={
                    'min':0,
                    'max':8
                }
            ),
            'workDoneAndResults':forms.NumberInput(
                attrs={
                    'min':0,
                    'max':12
                }
            ),
            'exceptionalWork':forms.NumberInput(
                attrs={
                    'min':0,
                    'max':6
                }
            ),
            'vivaVoce':forms.NumberInput(
                attrs={
                    'min':0,
                    'max':8
                }
            ),
            'presentation':forms.NumberInput(
                attrs={
                    'min':0,
                    'max':4
                }
            ),
            'report':forms.NumberInput(
                attrs={
                    'min':0,
                    'max':2
                }
            )
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            
            for field in self.fields:
                self.fields[field].initial = getattr(instance, field)
        for name,field in self.fields.items():
            field.widget.attrs.update({'class':'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'})
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
            'datetime_from': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-input'}),
            'datetime_to': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-input'}),
            'depthOfUnderstanding':forms.NumberInput(
                attrs={
                    'min':0,
                    'max':12
                }
            ),
            'workDoneAndResults':forms.NumberInput(
                attrs={
                    'min':0,
                    'max':18
                }
            ),
            'exceptionalWork':forms.NumberInput(
                attrs={
                    'min':0,
                    'max':6
                }
            ),
            'vivaVoce':forms.NumberInput(
                attrs={
                    'min':0,
                    'max':12
                }
            ),
            'presentation':forms.NumberInput(
                attrs={
                    'min':0,
                    'max':6
                }
            ),
            'report':forms.NumberInput(
                attrs={
                    'min':0,
                    'max':3
                }
            ),
            'attendance':forms.NumberInput(
                attrs={
                    'min':0,
                    'max':3
                }
            )
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            for field in self.fields:
                self.fields[field].initial = getattr(instance, field)
        for name,field in self.fields.items():
            field.widget.attrs.update({'class':'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'})
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
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = Student
        fields = ['name', 'email', 'rollno','cgpa']
        widgets={
            'cgpa':forms.NumberInput(
                attrs={
                    'min':0.0,
                    'max':10.0
                }
            ),
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
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = Faculty
        fields = ['name', 'email', 'facultyID']

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

