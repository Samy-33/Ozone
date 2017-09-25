from django.shortcuts import render
from django.utils import timezone

from inout.decorators import is_activated

from .models import ProblemTag, Tag


@is_activated
def index(request):

    tags = Tag.objects.all()
    return render(request, 'practice/index.html', {'tags': tags})


@is_activated
def get_tag(request, code):
    tag = Tag.objects.get(code=code)
    now = timezone.now()
    problems = filter(lambda t: now > t.problem.contest.end_date,
                      ProblemTag.objects.filter(tag=tag))

    return render(request, 'practice/problems.html', {'problems': problems, 'tag': tag.name})
