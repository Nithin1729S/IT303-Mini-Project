from django.db import models
from users.models import Profile,Student,Faculty
from django.core.validators import FileExtensionValidator,MinValueValidator, MaxValueValidator
import uuid


class Project(models.Model):
    id = models.UUIDField(default=uuid.uuid4,unique=True,primary_key=True,editable=False)
    title=models.CharField(max_length=255)
    desc=models.TextField(null=True,blank=True)
    src_link=models.CharField(max_length=2000,null=True,blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='projects')
    submitted_at = models.DateTimeField(auto_now_add=True)
    examiner = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, related_name='examiner_projects')
    guide = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, related_name='guide_projects')
    
    def __str__(self):
        return f"{self.title}"
    

class GuideEvaluation(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='guide_evaluation')
    guide = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    datetime_from=models.DateTimeField(null=True,blank=True)
    datetime_to=models.DateTimeField(null=True,blank=True)
    # Example metrics specific to Guide
    depthOfUnderstanding = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(12)])
    workDoneAndResults = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(18)])
    exceptionalWork = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(6)])
    vivaVoce = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(12)])
    presentation = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(6)])
    report = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(3)])
    attendance = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(3)])
    comments = models.TextField(blank=True, null=True)

    @property
    def total_score(self):
        return (self.depthOfUnderstanding + self.workDoneAndResults +
                self.exceptionalWork + self.vivaVoce +
                self.presentation + self.report + self.attendance)

    def __str__(self):
        return f"Guide Evaluation for {self.project.title}"
    
class ExaminerEvaluation(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='examiner_evaluation')
    examiner = models.ForeignKey(Faculty, on_delete=models.CASCADE, limit_choices_to={'profile__role': 'faculty'})
    datetime_from=models.DateTimeField(null=True,blank=True)
    datetime_to=models.DateTimeField(null=True,blank=True)
    # Example metrics specific to Examiner
    depthOfUnderstanding = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(8)])
    workDoneAndResults = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(12)])
    exceptionalWork = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(6)])
    vivaVoce = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(8)])
    presentation = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(4)])
    report = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(2)])
    comments = models.TextField(blank=True, null=True)
    @property
    def total_score(self):
        return (self.depthOfUnderstanding + self.workDoneAndResults +
                self.exceptionalWork + self.vivaVoce +
                self.presentation + self.report)
    def __str__(self):
        return f"Examiner Evaluation for {self.project.title}"


