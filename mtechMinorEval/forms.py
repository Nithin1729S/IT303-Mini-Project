from django.forms import ModelForm
from django.forms.widgets import NumberInput
from django import forms
from .models import ExaminerEvaluation,GuideEvaluation
class ExaminerEvaluationForm(ModelForm):
    class Meta:
        model=ExaminerEvaluation
        exclude=[]
        fields=['datetime_from','datetime_to','depthOfUnderstanding','workDoneAndResults','exceptionalWork','vivaVoce','presentation','report','comments']
        widgets={
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
            # If we're editing an existing instance, populate the initial data
            for field in self.fields:
                self.fields[field].initial = getattr(instance, field)
        for name,field in self.fields.items():
            field.widget.attrs.update({'class':'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'})
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
        fields=['datetime_from','datetime_to','depthOfUnderstanding','workDoneAndResults','exceptionalWork','vivaVoce','presentation','report','attendance','comments']
        widgets={
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
            # If we're editing an existing instance, populate the initial data
            for field in self.fields:
                self.fields[field].initial = getattr(instance, field)
        for name,field in self.fields.items():
            field.widget.attrs.update({'class':'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'})
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.instance.pk is None:  # This is a new evaluation
            instance.project = self.initial['project']
            instance.guide = self.initial['guide']
        if commit:
            instance.save()
        return instance