import re
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from .models import *

class DateInput(forms.DateInput):
    input_type = 'date'

class RegistrationForm(forms.Form):
	username = forms.RegexField(regex=r'^\w+$', widget=forms.TextInput(attrs=dict(required=True, max_lenght=20)), label=_('Username'), error_messages={'invalid':_("This is not a valid username [Only letters and digits allowed]")})
	hd = forms.RegexField(regex=r'^\w+$', widget=forms.TextInput(attrs=dict(required=True, max_length=10)), label=_("Ozone Hadle"))
#	name = forms.CharField(widget=forms.TextInput(attrs=dict(required=True, max_length=30)), label=_('Name'))
	fname = forms.CharField(widget=forms.TextInput(attrs=dict(required=True, max_length=20)), label=_("First Name"))
	lname = forms.CharField(widget=forms.TextInput(attrs=dict(required=True, max_length=20)), label=_("Last Name"))
	dob = forms.DateTimeField(widget=forms.DateInput(attrs=dict(required=False, placeholder="YYYY-MM-DD")), label=_("Date of Birth"))
	password1 = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=True)), label=_("Password"))
	password2 = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=True)), label=_("Repeat Password"))

	
	def clean_username(self):
		try:
			user = User.objects.get(username__iexact=self.cleaned_data['username'])
		except User.DoesNotExist:
			return self.cleaned_data['username']
		raise forms.ValidationError(_("Username already exists. You can't register twice."))
	
	def clean_hd(self):
		try:
			p = Profile.objects.get(hd__iexact=self.cleaned_date['hd'])
		except:
			return self.cleaned_data['hd']
		raise forms.ValidationError(_("Handle already exists."))
	
	def clean(self):
		if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
			if self.cleaned_data['password1'] != self.cleaned_data['password2']:
				raise forms.ValidationError(_("Passwords do not match."))
		return self.cleaned_data
	
class ActivateForm(forms.Form):
	act_code = forms.CharField(widget=forms.TextInput(attrs=dict(required=True, max_length=6)), label=_("Activation Code"))
	

	
languages = (
	('cpp', 'c++'),
	('c', 'c'),
	('python2', 'python2.7'),
	('python3', 'python3.7'),
	('java', 'java'),
)
	
class CodeForm(forms.Form):
	language=forms.ChoiceField(choices=languages, required=True)
	code = forms.CharField(widget=forms.Textarea(attrs={'required':'False', 'max_length':1500, 'class':"code"}), label=_("Code"))
	inpt = forms.CharField(widget=forms.Textarea(attrs={'max_length':100, 'class':"input"}), label=_("Input"))