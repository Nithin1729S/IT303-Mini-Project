from django.contrib import admin

# Register your models here.
from .models import Project,Profile,Student,Faculty,ExaminerEvaluation,GuideEvaluation,ProjectEvalSummary
admin.site.register(Project)
admin.site.register(ExaminerEvaluation)
admin.site.register(GuideEvaluation)
admin.site.register(ProjectEvalSummary)