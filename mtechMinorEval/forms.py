from django.forms import ModelForm
from .models import ExaminerEvaluation,GuideEvaluation

class ExaminerEvaluationForm(ModelForm):
    class Meta:
        model=ExaminerEvaluation
        exclude=['project','examiner']


class GuideEvaluationForm(ModelForm):
    class Meta:
        model=GuideEvaluation
        exclude=['project','guide']