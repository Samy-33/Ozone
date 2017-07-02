from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Contest, Problem
from inout.global_vars import *
import datetime
from django.db.models import Q
from .forms import *
from django.contrib.auth.models import User
import pytz
from django.views.decorators.csrf import csrf_protect
from inout.global_func import aware
from time import sleep
import subprocess as sb

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
		if(con.end_date >= aware(datetime.datetime.now())): aled = True
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
				import os
				pt = os.getcwd()
				path = os.path.join(pt, "tmp/problems/%s"%(pb.code))
				os.makedirs(path)
				pb.save()
				
				for file in request.FILES:
					with open(os.path.join(path, file), "w") as f:
						for kk in request.FILES[file].readlines():
							f.write(str(kk))
					
				
				
				return redirect('/contests/q/%s/'%code)
			else:
				return render(request, 'contests/', {'form':form})
		except Exception as e:
			return render(request, 'contests/addq.html', {'form':Prob(initial={})})
	return render(request, 'contests/addq.html', {'form':Prob(initial={})})

"""
## This whole region is for checking the user's output agains the given test outputs

"""


@csrf_protect
@login_required(login_url="/")
def submit(request, code):
	if(request.method == 'POST'):
		q = get_object_or_404(Problem, code=code)

		import os
		path_for_problem = os.path.join(os.getcwd(), "tmp/%s/%s"%(request.user.username, code))
		if(not os.path.exists(path_for_problem)):
			os.makedirs(path_for_problem)
		path_for_tests = os.path.join(os.getcwd(), "tmp/problems/%s"%(code))
		codepath = os.path.join(path_for_problem, "code%s"%(extensions[request.POST.get('lang')]))
		outputpath = os.path.join(path_for_problem, output[request.POST.get('lang')])
		
		with open(codepath, "w") as file:
			file.write(request.POST.get('code'))
		for i in range(0, q.n_testfiles+1):
			"""
			## This is compiling the code
			"""
			try:
				compile_cmd = cmds[request.POST.get('lang')][0]
				if(request.POST.get('lang') in ['c', 'cpp']):
					compile_cmd = compile_cmd%(codepath, outputpath)
				else:
					compile_cmd = compile_cmd%(codepath)
				compile_cmd = "timeout 2s "+compile_cmd
				## Not secure
				sb.check_output(compile_cmd.strip(), shell=True, stderr=sb.STDOUT)
				
			except sb.CalledProcessError as e:
				if("status 124" not in str(e)):
					removeDir(request, code)
					retdata = "<pre>%s</pre>"%("<br>".join(e.output.split("\n")))
					return JsonResponse({'status':'compile_error', 'error':retdata})
			"""
			## Ending the compilation process If successful, move on to run the code and output
			"""
			try:
				run_cmd = "timeout "+str(q.time_lim)+"s time "+(cmds[request.POST.get('lang')][1]%(outputpath, \
																								  os.path.join(path_for_tests, 'in%d.txt'%i), \
																								  os.path.join(path_for_problem, 'uout%d.txt'%i)))
				### Not Secure
				res = sb.check_output(run_cmd.strip(), shell=True, stderr=sb.STDOUT)
					
				retcode = check(request.user, q.code, i)
				removeDir(request, code)
				if(retcode==1):
					res = res.split()[1]
					res = res.split('s')[0]
					return JsonResponse({"status":"accepted", "error":"Time Taken:"+res+"s"})
				elif(retcode==0):
					return JsonResponse({"status":"wrong_answer", "error":"WA in testcase %d"%i})
				else:
					return JsonResponse({"status":"System_error", "error":"Results can't be matched properly"})
			except sb.CalledProcessError as e:
				if("status 124" in str(e)):
					removeDir(request, code)
					return JsonResponse({"status":"time_limit_exceeded", "error":"TLE %s"%(q.time_lim)})
				if("status 1" in str(e)):
					removeDir(request, code)
					return JsonResponse({"status":"run_time_error", "error":"Run Time Error"})
	removeDir(request, code)
	return HttpResponse("Still to add this code, going to be long. I guess.")


def removeDir(request, code):
	import os, shutil
	path_to_clear = os.path.join(os.getcwd(), "tmp/%s/%s"%(request.user.username,code))
	if(os.path.exists(path_to_clear)):
		shutil.rmtree(path_to_clear)
	
	
def check(user, problem, n):
	try:
		import os
		user_output = open(os.path.join(os.getcwd(), "tmp/%s/%s/uout%d.txt"%(user, problem, n)), "r")
		exp_output = open(os.path.join(os.getcwd(), "tmp/problems/%s/out%d.txt"%(problem, n)), "r")
		c1, c2 = "1", "1"
		while c1 != "" or c2 != "":
			c1 = user_output.readline().strip()
			c2 = exp_output.readline().strip()
			if(c1 != c2):
				return 0
		return 1
	except Exception as e:
		return 2
		


"""

## Here is the end of Submission check view and related functions

"""


def deleteq(request, code):
	q = get_object_or_404(Problem, code=code)
	
	if(q.contest.admin == request.user):
		q.delete()
		import os
		try:
			import shutil
			shutil.rmtree("./tmp/problems/%s"%code)
		except:
			pass
	else:
		raise Http404
	return HttpResponse("Done")