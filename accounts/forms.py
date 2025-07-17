from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from .models import UserProfile


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control form-control-glass',
                'placeholder': ' '
            })
class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['username'].widget.attrs.update({
            'class': 'form-control form-control-glass',
            'placeholder': ' '
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control form-control-glass',
            'placeholder': ' '
        })

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control form-control-glass',
                'placeholder': ' '
            })

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control form-control-glass',
                'placeholder': ' '
            })