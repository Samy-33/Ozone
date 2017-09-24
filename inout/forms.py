import re
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from .models import *

class DateInput(forms.DateInput):
    input_type = 'date'


class RegistrationForm(forms.Form):
    username = forms.RegexField(
        regex=r'^\w+$',
        widget=forms.TextInput(attrs={'required': True, 'max_length': 20, 'class': 'form-control',
                                      'id': 'rusername','placeholder': 'Username'}),
        label=_('Username'),
        error_messages={'invalid': ("This is not a valid username [Only letters and digits allowed]")}
    )
    fname = forms.CharField(
        widget=forms.TextInput(attrs={'required': True, 'maxlength': 20, 'class': 'form-control',
                                      'id': 'rfname','placeholder': 'First Name'}),
        label=_("First Name")
    )
    lname = forms.CharField(
        widget=forms.TextInput(attrs={'required': True, 'maxlength': 20, 'class': 'form-control',
                                      'id': 'rlname', 'placeholder': 'Last Name'}),
        label=_("Last Name")
    )
    dob = forms.DateTimeField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'rdob'}),
        label=_("Date of Birth"),
        required=False
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'required': True, 'minlength': 8, 'maxlength': 30,
                                          'render_value': True, 'class': 'form-control',
                                          'id': 'rpassword1', 'placeholder': 'Password (8-30 characters)'}),
        label=_("Password")
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'required': True, 'minlength': 8, 'maxlength': 30,
                                          'render_value': True, 'class': 'form-control',
                                          'id': 'rpassword2', 'placeholder': 'Repeat Password'}),
        label=_("Repeat Password")
    )


    def clean_username(self):
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['username'])
            raise forms.ValidationError(_("Username already exists. You can't register with same username."))
        except User.DoesNotExist:
            pass

        if not self.cleaned_data['username'].isalnum():
            raise forms.ValidationError(_("Username must be alphanumeric."))

        return self.cleaned_data['username']

    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("Passwords do not match."))
        return self.cleaned_data


class ActivateForm(forms.Form):
    act_code = forms.CharField(
        widget=forms.TextInput(attrs={ 'maxlength': 6, 'class': "activate-input form-control" }),
        label=_("Activation Code"),
        required=False
    )


class CodeForm(forms.Form):
    LANGUAGES = (
        ('cpp', 'C++'),
        ('c', 'C'),
        ('python2', 'Python 2.7'),
        ('python3', 'Python 3.7'),
        ('java', 'Java'),
    )

    language = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        choices=LANGUAGES
    )
    code = forms.CharField(
        widget=forms.Textarea(attrs={'max_length': 5000, 'class': "codebox form-control"}),
        label=_("Code")
    )
    inpt = forms.CharField(
        widget=forms.Textarea(attrs={'max_length': 100, 'rows': 3, 'class': "codebox form-control"}),
        label=_("Input"),
        required=False
    )
