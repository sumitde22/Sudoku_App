from django import forms

class UserForm(forms.Form):
    email = forms.EmailField()
    username = forms.CharField()
    password = forms.CharField()