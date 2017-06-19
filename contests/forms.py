import re
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from .models import Contest

class CreateContest(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(CreateContest, self).__init__(*args, **kwargs)
		self.fields['start_date'].widget.attrs['placeholder']="YYYY-MM-DD HH:mm"
		self.fields['end_date'].widget.attrs['placeholder']="YYYY-MM-DD HH:mm"
	
	class Meta:
		model=Contest
		fields=['name', 'contest_code', 'start_date', 'end_date']
	