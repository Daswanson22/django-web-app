from django import forms

class CreateQuestionForm(forms.Form):
    question_text = forms.CharField()
    pub_date = forms.DateField()
    