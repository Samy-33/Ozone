import re
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from .models import Contest, Problem

class CreateContest(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(CreateContest, self).__init__(*args, **kwargs)
		self.fields['start_date'].widget.attrs['placeholder']="YYYY-MM-DD HH:mm"
		self.fields['end_date'].widget.attrs['placeholder']="YYYY-MM-DD HH:mm"
	
	class Meta:
		model=Contest
		fields=['name', 'contest_code', 'start_date', 'end_date']
		
	def clean_contest_code(self):
		
		try:
			c = Contest.objects.get(contest_code=self.cleaned_data['contest_code'])
			raise forms.ValidationError("A Contest with same contest code already exists.")
		except:
			return self.cleaned_data['contest_code']
	
class Prob(forms.ModelForm):
#	code = forms.CharField(widget=forms.TextInput(attrs=dict(required=True, max_length=10)), label="Problem Code")
	text = forms.CharField(widget=forms.Textarea)
	class Meta:
		model = Problem
		fields=['code', 'name', 'time_lim', 'text']
	
	def clean_code(self):
		try:
			q = Problem.objects.get(code=self.cleaned_data['code'])
			raise forms.ValidationError("A problem with this code already exists.")
		except:
			return self.cleaned_data['code']
	
#	
#		username = forms.RegexField(regex=r'^\w+$', widget=forms.TextInput(attrs=dict(required=True, max_lenght=20)), label=_('Username'), error_messages={'invalid':_("This is not a valid username [Only letters and digits allowed]")})
#	hd = forms.RegexField(regex=r'^\w+$', widget=forms.TextInput(attrs=dict(required=True, max_length=10)), label=_("Ozone Hadle"))
##	name = forms.CharField(widget=forms.TextInput(attrs=dict(required=True, max_length=30)), label=_('Name'))
#	fname = forms.CharField(widget=forms.TextInput(attrs=dict(required=True, max_length=20)), label=_("First Name"))
#	lname = forms.CharField(widget=forms.TextInput(attrs=dict(required=True, max_length=20)), label=_("Last Name"))
#	dob = forms.DateTimeField(widget=forms.DateInput(attrs=dict(required=False, placeholder="YYYY-MM-DD")), label=_("Date of Birth"))
#	password1 = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=True)), label=_("Password"))
#	password2 = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=True)), label=_("Repeat Password"))
#
#	