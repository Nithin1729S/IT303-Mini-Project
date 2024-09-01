from django.forms import ModelForm
from .models import ExaminerEvaluation,GuideEvaluation

class ExaminerEvaluationForm(ModelForm):
    class Meta:
        model=ExaminerEvaluation
        exclude=[]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            # If we're editing an existing instance, populate the initial data
            for field in self.fields:
                self.fields[field].initial = getattr(instance, field)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.instance.pk is None:  # This is a new evaluation
            instance.project = self.initial['project']
            instance.examiner = self.initial['examiner']
        if commit:
            instance.save()
        return instance

class GuideEvaluationForm(ModelForm):
    class Meta:
        model=GuideEvaluation
        exclude=[]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            # If we're editing an existing instance, populate the initial data
            for field in self.fields:
                self.fields[field].initial = getattr(instance, field)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.instance.pk is None:  # This is a new evaluation
            instance.project = self.initial['project']
            instance.guide = self.initial['guide']
        if commit:
            instance.save()
        return instance