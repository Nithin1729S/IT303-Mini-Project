from django.contrib import admin

# Register your models here.
from .models import Project,Profile,Student,Faculty,ExaminerEvaluation,GuideEvaluation
admin.site.register(Project)
admin.site.register(ExaminerEvaluation)
admin.site.register(GuideEvaluation)