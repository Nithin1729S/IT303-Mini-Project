from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import Profile,Student,Faculty
from django.core.validators import FileExtensionValidator,MinValueValidator, MaxValueValidator
import uuid
from django.core.exceptions import ValidationError
from django.utils import timezone

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


class ProjectEvalSummary(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='eval_summary')
    project_name = models.CharField(max_length=255)
    examiner_total_eval = models.PositiveIntegerField(default=0)
    guide_total_eval = models.PositiveIntegerField(default=0)
    is_satisfactory = models.BooleanField(default=False)
    guide_name = models.CharField(max_length=255, blank=True)
    examiner_name = models.CharField(max_length=255, blank=True)
    student_rollno = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"Evaluation Summary for {self.project_name}"

def create_or_update_eval_summary(project):
    summary, created = ProjectEvalSummary.objects.get_or_create(project=project)
    summary.project_name = project.title
    summary.guide_name = project.guide.profile.user.get_full_name() if project.guide else ""
    summary.examiner_name = project.examiner.profile.user.get_full_name() if project.examiner else ""
    summary.student_rollno = project.student.rollno if hasattr(project.student, 'rollno') else ""
    summary.save()
    return summary

@receiver(post_save, sender=Project)
def project_post_save(sender, instance, created, **kwargs):
    create_or_update_eval_summary(instance)

@receiver(post_save, sender=GuideEvaluation)
def update_guide_eval(sender, instance, **kwargs):
    summary = create_or_update_eval_summary(instance.project)
    summary.guide_total_eval = instance.total_score
    summary.is_satisfactory = (summary.guide_total_eval + summary.examiner_total_eval) >= 50  # Adjust threshold as needed
    summary.save()

@receiver(post_save, sender=ExaminerEvaluation)
def update_examiner_eval(sender, instance, **kwargs):
    summary = create_or_update_eval_summary(instance.project)
    summary.examiner_total_eval = instance.total_score
    summary.is_satisfactory = (summary.guide_total_eval + summary.examiner_total_eval) >= 50  # Adjust threshold as needed
    summary.save()

# Run this function once to create ProjectEvalSummary for existing Projects
def create_eval_summaries_for_existing_projects():
    for project in Project.objects.all():
        create_or_update_eval_summary(project)
