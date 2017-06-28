from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Contest, Problem
import datetime
from django.db.models import Q
from .forms import *
from django.contrib.auth.models import User
# Create your views here.


@login_required(login_url='/')
def index(request):
	now = datetime.datetime.now()
#	upcoming = Contest.objects.filter(allowed=1)
#	print(upcoming)
#	current = upcoming[:]
	try:
#		upcoming = Contest.objects.filter(allowed=0)
		upcoming = Contest.objects.filter(Q(start_date__gt=datetime.datetime.now())&Q(allowed=1)).order_by('-start_date')
	except:
		upcoming = []
	try:
#		current = Contest.objec
		current = Contest.objects.filter(Q(start_date__lte=datetime.datetime.now())&Q(end_date__gt=datetime.datetime.now())&Q(allowed=1)).order_by('-start_date')
	except:
		current = []
	try:
		usrs_contest = Contest.objects.get(username=request.user.username)
	except:
		usrs_contest = []
	return render(request, 'contests/contests.html', {'upcoming':upcoming, 'current':current, 'usrs_contest':usrs_contest})
#	return HttpResponse("Welcome %s, This is Contest Page."%(str(request.user.username)))

@login_required(login_url='/')
def create(request):
	if(request.method == 'POST'):
		form = CreateContest(request.POST)
		if(form.is_valid()):
#			stdt = datetime.datetime.strptime(form.cleaned_data['start_date'], "%Y-%m-%d %H:%M")
#			endt = datetime.datetime.strptime(form.cleaned_data['end_date'], "%Y-%m-%d %H:%M")
			p1 = form.cleaned_data['start_date']
			p2 = form.cleaned_data['end_date']
#			p1.tzinfo = 'ist'
#			p2.tzinfo = 'ist'
			c = Contest.objects.create(
				admin = request.user,
				name = form.cleaned_data['name'],
				contest_code=form.cleaned_data['contest_code'],
				start_date=p1,
				end_date=p2,
				allowed=0,
			)
			request.user.profile.tobecon = True
			request.user.save()
			c.save()
			form = CreateContest(initial={})
			return render(request, 'contests/create_contest.html', {'form':form})
		else:
			return render(request, 'contests/create_contest.html', {'form':CreateContest(initial={})})
	else:
		form = CreateContest(initial={})
		return render(request, 'contests/create_contest.html', {'form':form})
#	return HttpResponse("Welcome, here you can create your own contests!")

@login_required(login_url="/")
def contest(request, code=None):
	return HttpResponse("Ok!!")