from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Question,Answer,Profile,Approved

class NewQuestionForm(forms.ModelForm):
    snippet = forms.ImageField(required=False)
    class Meta:
        model = Question
        exclude = ['user']

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('answer',)
        widgets = {
            'answer': forms.Textarea(attrs={'cols': 30, 'rows': 3})
            }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ['user']

class ApproveForm(forms.ModelForm):
    class Meta:
        model = Approved
        fields = ['approve']

class UserRegistrationForm(UserCreationForm):
    email=forms.EmailField()
    class Meta:
        model=User
        fields=['username','email','password1','password2']

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
