from django.contrib import admin

# Register your models here.
from .models import Project,ExaminerEvaluation,GuideEvaluation,ProjectEvalSummary,ActivityLog
admin.site.register(Project)
admin.site.register(ExaminerEvaluation)
admin.site.register(GuideEvaluation)
admin.site.register(ProjectEvalSummary)
admin.site.register(ActivityLog)