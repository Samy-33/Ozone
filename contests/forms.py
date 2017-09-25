from django import forms
from django.contrib.admin import widgets
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from practice.models import Tag

from .models import Contest, Problem


class CreateContest(forms.Form):

    name = forms.CharField(widget=forms.TextInput(attrs={'max_length': 30,
                                                         'class': 'form-control'}),
                           label=_("Name"))

    contest_code = forms.CharField(
                            widget=forms.TextInput(
                                            attrs={'max_length': 30,
                                                   'class': 'form-control'}),
                            label="Contest Code")
    start_date = forms.SplitDateTimeField(widget=widgets.AdminSplitDateTime())
    end_date = forms.SplitDateTimeField(widget=widgets.AdminSplitDateTime())

    def clean_contest_code(self):
        try:
            Contest.objects.get(contest_code=self.cleaned_data['contest_code'])
            raise forms.ValidationError("A Contest with same contest code already exists.")
        except:
            if len(self.cleaned_data['contest_code']) < 4:
                raise forms.ValidationError("Contest Code must be at least 4 letters long.")
            return self.cleaned_data['contest_code']

    def clean(self):
        super(CreateContest, self).clean()
        now = timezone.now()
        if now >= self.cleaned_data['start_date']:
            raise forms.ValidationError("Past dates are not allowed.")

        condition = self.cleaned_data['end_date'] <= self.cleaned_data['start_date']
        if now >= self.cleaned_data['end_date'] or condition:
            raise forms.ValidationError("Invalid time")

        return self.cleaned_data


class Prob(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(Prob, self).__init__(*args, **kwargs)
        for field in self.fields:
            if field == 'tags':
                continue
            self.fields[field].widget.attrs['class'] = 'form-control'

    try:
        choices = tuple((tag.id, tag.name) for tag in Tag.objects.all())
    except:
        choices = []
    text = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    tags = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=choices)

    class Meta:
        model = Problem
        fields = ['code', 'name', 'n_testfiles', 'time_lim', 'score', 'text']

    def clean_code(self):
        try:
            Problem.objects.get(code=self.cleaned_data['code'])
            raise forms.ValidationError("A problem with this code already exists.")
        except:
            if len(self.cleaned_data['code']) < 4:
                raise forms.ValidationError("Problem Code must be at least 4 letters long.")
            return self.cleaned_data['code']


class EditProb(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(EditProb, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    text = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Problem
        fields = ['name', 'n_testfiles', 'time_lim', 'score', 'text']
