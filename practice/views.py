from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Tag, ProblemTag
from datetime import datetime as dt
from inout.global_func import aware
# Create your views here.


@login_required(login_url='/')
def index(request):

    tags = Tag.objects.all()	
    return render(request, 'practice/index.html', {'tags':tags})


@login_required(login_url='/')
def get_tag(request, code):
    tag = Tag.objects.get(code=code)
    now = aware(dt.now())
    problems = filter(lambda t: now > t.problem.contest.end_date,
                      ProblemTag.objects.filter(tag=tag))

    return render(request, 'practice/problems.html', {'problems':problems})