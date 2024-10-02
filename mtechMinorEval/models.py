from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import Profile,Student,Faculty
from django.core.validators import FileExtensionValidator,MinValueValidator, MaxValueValidator
import uuid
from django.core.exceptions import ValidationError
from django.utils import timezone

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import Student, Faculty


class Project(models.Model):
    id = models.UUIDField(default=uuid.uuid4,unique=True,primary_key=True,editable=False)
    title=models.CharField(max_length=255)
    desc=models.TextField(null=True,blank=True)
    src_link=models.CharField(max_length=2000,null=True,blank=True)
    ppt=models.FileField(upload_to='mtechMinorEval/ppts/',null=True,blank=True)
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='projects')
    submitted_at = models.DateTimeField(auto_now_add=True)
    examiner = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, related_name='examiner_projects')
    guide = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, related_name='guide_projects')
    deadline=models.DateTimeField(null=True,blank=True)
    def __str__(self):
        return f"{self.title}"
    def clean(self):
        super().clean()
        # Ensure the examiner and guide are different entities
        if self.examiner == self.guide:
            raise ValidationError("The examiner and guide must be different.")
        
        if self.deadline and self.deadline <= timezone.now():
            raise ValidationError("The deadline must be a future date and time.")


    def save(self, *args, **kwargs):
        # Call the model's clean method before saving to ensure validation
        self.clean()
        super().save(*args, **kwargs)
    

class GuideEvaluation(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='guide_evaluation')
    guide = models.ForeignKey(Faculty, on_delete=models.SET_NULL,null=True,blank=True)
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
    examiner = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True,blank=True,limit_choices_to={'profile__role': 'faculty'})
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



from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class ProjectEvalSummary(models.Model):
    project = models.OneToOneField('Project', on_delete=models.CASCADE, related_name='eval_summary')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    guide = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, related_name='guide_eval_summaries')
    examiner = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, related_name='examiner_eval_summaries')
    examiner_score = models.PositiveIntegerField(default=0)
    guide_score = models.PositiveIntegerField(default=0)
    total_score = models.PositiveIntegerField(default=0)
    sn = models.CharField(max_length=1, editable=False, default='n')

    def save(self, *args, **kwargs):
        self.total_score = self.guide_score + self.examiner_score
        self.sn = 'S' if self.total_score >= 50 else 'N'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Evaluation Summary for {self.project.title}"

@receiver(post_save, sender='mtechMinorEval.Project')
def create_or_update_eval_summary(sender, instance, created, **kwargs):
    eval_summary, _ = ProjectEvalSummary.objects.get_or_create(project=instance)
    eval_summary.student = instance.student
    eval_summary.guide = instance.guide
    eval_summary.examiner = instance.examiner
    eval_summary.save()

@receiver(post_save, sender='mtechMinorEval.GuideEvaluation')
def update_guide_evaluation(sender, instance, **kwargs):
    eval_summary, _ = ProjectEvalSummary.objects.get_or_create(project=instance.project)
    eval_summary.student = instance.project.student
    eval_summary.guide = instance.guide
    eval_summary.guide_score = instance.total_score
    eval_summary.save()

@receiver(post_save, sender='mtechMinorEval.ExaminerEvaluation')
def update_examiner_evaluation(sender, instance, **kwargs):
    eval_summary, _ = ProjectEvalSummary.objects.get_or_create(project=instance.project)
    eval_summary.student = instance.project.student
    eval_summary.examiner = instance.examiner
    eval_summary.examiner_score = instance.total_score
    eval_summary.save()

from django.db import models

class PathAccess(models.Model):
    path = models.CharField(max_length=255)
    access_count = models.IntegerField(default=0)
    bounces = models.IntegerField(default=0)  # New field to track bounces

    def __str__(self):
        return self.path
