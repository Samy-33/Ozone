import re, datetime
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from .models import Contest, Problem
from inout.global_func import aware
from django.contrib.admin import widgets

class CreateContest(forms.Form):
	
	name = forms.CharField(widget=forms.TextInput(attrs=dict(max_length=30)), label="Name")
	contest_code = forms.CharField(widget=forms.TextInput(attrs=dict(max_length=30)), label="Contest Code")
	start_date = forms.SplitDateTimeField(widget=widgets.AdminSplitDateTime())
	end_date = forms.SplitDateTimeField(widget=widgets.AdminSplitDateTime())

	
	
	
#	username = forms.RegexField(regex=r'^\w+$', widget=forms.TextInput(attrs=dict(required=True, max_lenght=20)), label=_('Username'), error_messages={'invalid':_("This is not a valid username [Only letters and digits allowed]")})
#	fname = forms.CharField(widget=forms.TextInput(attrs=dict(required=True, max_length=20)), label=_("First Name"))
#	lname = forms.CharField(widget=forms.TextInput(attrs=dict(required=True, max_length=20)), label=_("Last Name"))
#	dob = forms.DateTimeField(widget=forms.DateInput(attrs=dict(required=False, placeholder="YYYY-MM-DD")), label=_("Date of Birth"))
#	password1 = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=True)), label=_("Password"))
#	password2 = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=True)), label=_("Repeat Password"))

	
	#	def __init__(self, *args, **kwargs):
#		super(CreateContest, self).__init__(*args, **kwargs)
#		self.fields['start_date'].widget = widgets.AdminSplitDateTime()
#		self.fields['end_date'].widget = widgets.AdminSplitDateTime()
##		self.fields['start_date'].widget.attrs['placeholder']="YYYY-MM-DD HH:mm"
##		self.fields['end_date'].widget.attrs['placeholder']="YYYY-MM-DD HH:mm"
#
#	
#	class Meta:
#		model=Contest
#		fields=['name', 'contest_code']#, 'start_date', 'end_date']
##		exclude = ('start_date', 'end_date', 'allowed', 'admin')
#		
##	def clean(self):
##		self.instance.start_date = self.cleaned_data.get('start_date')
##		self.instance.end_date = self.cleaned_data.get('end_date')
	def clean_contest_code(self):
		try:
			c = Contest.objects.get(contest_code=self.cleaned_data['contest_code'])
			raise forms.ValidationError("A Contest with same contest code already exists.")
		except:
			return self.cleaned_data['contest_code']
	def clean_start_date(self):
		now = aware(datetime.datetime.now())
		print(now, self.cleaned_data['start_date'])
		if(now>=self.cleaned_data['start_date']):
			raise forms.ValidationError("Past dates are not allowed.")
		return self.cleaned_data['start_date']
	
	def clean_end_date(self):
		now = aware(datetime.datetime.now())
#		print(self.cleaned_data)
		if(now>=self.cleaned_data['end_date'] or self.cleaned_data['end_date'] <= self.cleaned_data['start_date']):
			raise forms.ValidationError("Invalid time")
		return self.cleaned_data['end_date']


	
class Prob(forms.ModelForm):
	text = forms.CharField(widget=forms.Textarea)
	class Meta:
		model = Problem
		fields=['code', 'name', 'n_testfiles', 'time_lim', 'score','text']
	
	def clean_code(self):
		try:
			q = Problem.objects.get(code=self.cleaned_data['code'])
			raise forms.ValidationError("A problem with this code already exists.")
		except:
			return self.cleaned_data['code']
	
