import re, datetime
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from .models import Contest, Problem
from inout.global_func import aware

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
		fields=['code', 'name', 'n_testfiles', 'time_lim', 'text']
	
	def clean_code(self):
		try:
			q = Problem.objects.get(code=self.cleaned_data['code'])
			raise forms.ValidationError("A problem with this code already exists.")
		except:
			return self.cleaned_data['code']
	
