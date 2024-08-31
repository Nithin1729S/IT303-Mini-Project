from django.forms import ModelForm
from .models import ExaminerEvaluation,GuideEvaluation

class ExaminerEvaluationForm(ModelForm):
    class Meta:
        model=ExaminerEvaluation
        fields='__all__'


class GuideEvaluationForm(ModelForm):
    class Meta:
        model=GuideEvaluation
        fields='__all__'