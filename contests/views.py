from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Contest, Problem
import datetime
from django.db.models import Q
from .forms import *
from django.contrib.auth.models import User
import pytz
from django.views.decorators.csrf import csrf_protect



@login_required(login_url='/')
def index(request):

	try:
		upcoming = Contest.objects.filter(Q(start_date__gt=datetime.datetime.now())&Q(allowed=1)).order_by('-start_date')
	except:
		upcoming = []
	try:
		current = Contest.objects.filter(Q(start_date__lte=datetime.datetime.now())&Q(end_date__gt=datetime.datetime.now())&Q(allowed=1)).order_by('-start_date')
	except:
		current = []
	try:
		usrs_contest = Contest.objects.filter(Q(admin=request.user))
#		print usrs_contest
	except:
		usrs_contest = []
	return render(request, 'contests/contests.html', {'upcoming':upcoming, 'current':current, 'usrs_contest':usrs_contest})


@login_required(login_url='/')
def create(request):
	if(request.method == 'POST'):
		form = CreateContest(request.POST)
		if(form.is_valid()):
			c = Contest.objects.create(
				admin = request.user,
				name = form.cleaned_data['name'],
				contest_code=form.cleaned_data['contest_code'],
				start_date=form.cleaned_data['start_date'],
				end_date=form.cleaned_data['end_date'],
				allowed=0,
			)
			request.user.profile.tobecon = True
			request.user.save()
			c.save()
			form = CreateContest(initial={})
			
			return render(request, 'contests/create_contest.html', {'form':form, 'done':True})
		else:
			return render(request, 'contests/create_contest.html', {'form':form, 'done':False})
	else:
		form = CreateContest(initial={})
		return render(request, 'contests/create_contest.html', {'form':form, 'done':False})


@login_required(login_url="/")
def contest(request, code):
#	print(code)
	con = get_object_or_404(Contest, Q(contest_code=code))

	dt = datetime.datetime.now().replace(tzinfo=pytz.timezone('Asia/Kolkata'))-con.start_date.replace(tzinfo=pytz.timezone('Asia/Kolkata'))
	if(dt.days < 0 or dt.seconds < 0):
		pp = True
	else:
		pp = False
	return render(request, 'contests/contest.html', {'contest':con, 'pp':pp})


@login_required(login_url="/")
def editc(request, code):
	con = get_object_or_404(Contest, Q(contest_code=code)&Q(end_date__gte=datetime.datetime.now()))

	if(con.admin == request.user):
		if(con.end_date >= datetime.datetime.now()): aled = True
		else: aled = False
		return render(request, 'contests/editc.html', {'contest':con, 'aled':aled})
	return render(request, 'contests/editc.html', {'contest':False})


@login_required(login_url="/")
def editq(request, code, question):
	if(request.method=="POST"):
		pass
	return HttpResponse("Well, going to add it, soon")


@login_required(login_url="/")
def problem(request, code, question):
	con = get_object_or_404(Contest, contest_code=code)
	ques = get_object_or_404(Problem, code=question)
	return render(request, 'contests/problem.html', {'contest':con, 'ques':ques})



@login_required(login_url="/")
def addq(request, code):
	if(request.method=="POST"):
		try:
			con = Contest.objects.get(contest_code=code)
			form = Prob(request.POST)
			if form.is_valid():
				pb = Problem.objects.create(
					setter = request.user,
					contest = con,
					name = form.cleaned_data['name'],
					code = form.cleaned_data['code'],
					text = form.cleaned_data['text'],
					time_lim = form.cleaned_data['time_lim']
				)
				pb.save()
			else:
				return render(request, 'contests/addq.html', {'form':form})
		except Exception as e:
			print(str(e))
			return render(request, 'contests/addq.html', {'form':Prob(initial={})})
	return render(request, 'contests/addq.html', {'form':Prob(initial={})})

@csrf_protect
@login_required(login_url="/")
def submit(request, code):
	return HttpResponse("Still to add this code, going to be long. I guess.")