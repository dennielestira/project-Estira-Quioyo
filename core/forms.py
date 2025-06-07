from django import forms
from .models import Grade

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['student', 'quiz', 'activity', 'exam', 'score']

    def clean(self):
        cleaned_data = super().clean()
        quiz = cleaned_data.get('quiz')
        activity = cleaned_data.get('activity')
        exam = cleaned_data.get('exam')
        if not any([quiz, activity, exam]):
            raise forms.ValidationError("At least one of Quiz, Activity, or Exam must be selected.")
        return cleaned_data
