from django import forms
from django.forms import ModelForm
from .models import *
from django.contrib.auth.models import User

class ChangeProfilePictureForm(forms.Form):
    profile_image = forms.ImageField(required=True)

class PostForm(forms.ModelForm):
    text = forms.CharField(required=True, widget=forms.Textarea({
        "placeholder":"Write your status here...",
        "rows" : 3,
        }))
    image = forms.ImageField(required=False)

    class Meta:
        model = Post
        fields = ('text', 'image')
        exclude = ('user',)
