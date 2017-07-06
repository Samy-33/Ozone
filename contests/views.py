from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import (Contest, Problem,
					 Solve, Ranking,
					 CommentQ, CommentC,
					 ConvC, ConvQ,
					)
from inout.global_vars import *
from .forms import *
from inout.global_func import aware
from time import sleep
import datetime
import pytz
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
		rq = request.POST
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
					time_lim = form.cleaned_data['time_lim'],
					score = form.cleaned_data['score'],
					n_testfiles = form.cleaned_data['n_testfiles'],
				)
				import os
				pt = os.getcwd()
				path = os.path.join(pt, "tmp/problems/%s"%(pb.code))
				os.makedirs(path)
				
				for file in request.FILES:
					with open(os.path.join(path, file), "w") as f:
						for kk in request.FILES[file].readlines():
							f.write(str(kk))
					
				
				
				return redirect('/contests/q/%s/'%code)
			else:
				return render(request, 'contests/addq.html', {'form':form})
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
		from inout.views import is_alright
		if(not is_alright(request.POST.get('code'), request.POST.get('lang'))):
			return JsonResponse({"status":"Code execution failure", "Error":"Invalid Code."})
		tim = 0.0
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

		for i in range(0, q.n_testfiles):
			"""
			## This is compiling the code
			"""
			if 'python' not in request.POST.get('lang'):
				try:
					compile_cmd = cmds[request.POST.get('lang')][0]%(codepath, outputpath) if request.POST.get('lang') !='java' else "javac tmp/%s/%s/code.java"%(request.user.username, q.code)
					## Not secure
					sb.check_output(compile_cmd.strip(), shell=True, stderr=sb.STDOUT)
				except sb.CalledProcessError as e:
					removeDir(request, code)
					if("status 124" not in str(e)):
						retdata = "<pre>%s</pre>"%("<br>".join(e.output.split("\n")))
						return JsonResponse({'status':'compile_error', 'error':retdata})
				"""
				## Ending the compilation process If successful, move on to run the code and output
				"""
			## Separate Code for Python
			if 'python' in request.POST.get('lang'):
				run_cmd = "timeout "+str(q.time_lim)+"s time "+(cmds[request.POST.get('lang')][1]%(codepath, \
																								  os.path.join(path_for_tests, 'in%d.txt'%i), \
																								   os.path.join(path_for_problem, 'uout%d.txt'%i)))
				try:
					res = sb.check_output(run_cmd.strip(), shell=True, stderr=sb.STDOUT)
					retcode = check(request.user, q.code, i)
					if(retcode==1):
						res = res.split()[2]
						res = res.split('e')[0].split(":")[1]
						tim = max(tim, float(res))
					elif(retcode==0):
						removeDir(request, code)
						if((not already(request.user, q)) and q.contest.start_date<=aware(datetime.datetime.now()) and q.contest.admin != request.user):
							addWA(request, q)
						return JsonResponse({"status":"wrong_answer", "error":"WA in testcase %d"%(i+1)})
					else:
						removeDir(request, code)
						if((not already(request.user, q)) and q.contest.start_date<=aware(datetime.datetime.now()) and q.contest.admin != request.user):
							addWA(request, q)
						return JsonResponse({"status":"System_error", "error":"Results can't be matched properly"})
				except sb.CalledProcessError as e:
					removeDir(request, code)
					if("status 124" not in str(e)):
						retdata = "<pre>%s</pre>"%("<br>".join(e.output.split("\n")))
						return JsonResponse({'status':'compile_error', 'error':retdata})
					return JsonResponse({'status':'unknown_error', 'error':str(e)})
			else:
				try:
					if(request.POST.get('lang') == 'java'):
						outputpath = "tmp/%s/%s Main"%(request.user.username, q.code)
					run_cmd = "timeout "+str(q.time_lim)+"s time "+(cmds[request.POST.get('lang')][1]%(outputpath, \
																									  os.path.join(path_for_tests, 'in%d.txt'%i), \
																									  os.path.join(path_for_problem, 'uout%d.txt'%i)))
					### Not Secure
					res = sb.check_output(run_cmd.strip(), shell=True, stderr=sb.STDOUT)

					retcode = check(request.user, q.code, i)
					if(retcode==1):
						res = res.split()[2]
						res = res.split('e')[0].split(":")[1]
						tim = max(tim, float(res))
					elif(retcode==0):
						removeDir(request, code)
						if((not already(request.user, q)) and q.contest.start_date<=aware(datetime.datetime.now()) and q.contest.admin != request.user):
							addWA(request, q)
						return JsonResponse({"status":"wrong_answer", "error":"WA in testcase %d"%(i+1)})
					else:
						removeDir(request, code)
						return JsonResponse({"status":"System_error", "error":"Results can't be matched properly"})
				except sb.CalledProcessError as e:
					print(e)
					if("status 124" in str(e)):
						removeDir(request, code)
						if((not already(request.user, q)) and q.contest.start_date<=aware(datetime.datetime.now()) and q.contest.admin != request.user):
							addWA(request, q)
						return JsonResponse({"status":"time_limit_exceeded", "error":"TLE %s"%(q.time_lim)})
					if("status 1" in str(e)):
						removeDir(request, code)
						return JsonResponse({"status":"run_time_error", "error":"Run Time Error"})
		removeDir(request, code)
		if((not already(request.user, q)) and q.contest.start_date<=aware(datetime.datetime.now()) and q.contest.admin != request.user):
			addAC(request, q)
		return JsonResponse({"status":"Accepted", "error":"time take => %f"%tim})

	return  JsonResponse({'status':'No testcases', "error":"can't find any testcase for this problem"})


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
		
def already(user, q):
	return Solve.objects.filter(Q(problem=q)&Q(user=user)).exists()

def addAC(request, q):
	Solve.objects.create(user=request.user, problem=q)
	try:
		p = Ranking.objects.get(user=request.user, contest=q.contest)
		p.ac += 1
		p.score += q.score
		p.save()
	except:
		p = Ranking.objects.create(user=request.user, contest=q.contest)
		p.ac = 1
		p.score = q.score
		p.save()

def addWA(request, q):
	try:
		p = Ranking.objects.get(user=request.user, contest=q.contest)
		p.score -= 5
		p.wa += 1
		p.save()
	except:
		p = Ranking.objects.create(user=request.user, contest=q.contest)
		p.score = -5
		p.wa = 1
		p.save()
"""

## Here is the end of Submission check view and related functions

"""

@login_required(login_url='/')
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


@login_required(login_url='/')
def rankings(request, contest):
	con = get_object_or_404(Contest, contest_code=contest)
	if(con.start_date <= aware(datetime.datetime.now())):
		data = Ranking.objects.filter(Q(contest=con)).order_by('-score')
		return render(request, 'contests/ranking.html', {'con':data, 'contest':con})
	else:
		return render(request, 'contests/ranking.html', {'con':[], 'contest':con})

	

@login_required(login_url='/')
def deletec(request, contest):
	con = get_object_or_404(Contest, contest_code=contest)
	
	if(con.start_date >= aware(datetime.datetime.now())):
		request.user.profile.tobecon = False
		request.user.profile.save()
		con.delete()
		return JsonResponse({'done':'Yes, Did that.'}, status=200)
	return JsonResponse({'done':'Nope cant do that'}, status=200)


@login_required(login_url='/')
def boardC(request, contest):
	con = get_object_or_404(Contest, contest_code=contest)
	if(request.method=="POST"):
		CommentC.objects.create(
			contest=con,
			user=request.user,
			text = request.POST.get('com'),
		)
	comments_list = CommentC.objects.filter(Q(contest=con)).order_by("-timestamp")
	paginator = Paginator(comments_list, 10)
	page = request.GET.get('page')
	try:
		comments = paginator.page(page)
	except:
		comments = paginator.page(1)
	
	return render(request, 'contests/discussionC.html', {'comments':comments, 'con':con})
	
	
@login_required(login_url='/')
def boardQ(request, code):
	prob = get_object_or_404(Problem, code=code)
	if(request.method=="POST"):
		CommentQ.objects.create(
			problem=prob,
			user=request.user,
			text = request.POST.get('com'),
		)
	comments_list = CommentQ.objects.filter(Q(problem=prob)).order_by("-timestamp")
	paginator = Paginator(comments_list, 10)
	page = request.GET.get('page')
	try:
		comments = paginator.page(page)
	except:
		comments = paginator.page(1)
		
	return render(request, 'contests/discussionQ.html', {'comments':comments, 'prob':prob})


@login_required(login_url='/')
def convQ(request, question, pk):
	main_comment = get_object_or_404(CommentQ, id=pk)
	prob = get_object_or_404(Problem, code=question)
	conversation_list = ConvQ.objects.filter(Q(comment=main_comment)).order_by('timestamp')
	if(request.method=="POST"):
		ConvQ.objects.create(
			comment=main_comment,
			user=request.user,
			text=request.POST.get('com'),
		)
	paginator = Paginator(conversation_list, 10)
	page = request.GET.get('page')
	try:
		conversations = paginator.page(page)
	except:
		conversations = paginator.page(1)
	
	return render(request, 'contests/convQ.html', {'conversations':conversations, 'prob':prob, 'main':main_comment})


@login_required(login_url='/')
def convC(request, code, pk):
	main_comment = get_object_or_404(CommentC, id=pk)
	con = get_object_or_404(Contest, contest_code=code)
	conversation_list = ConvC.objects.filter(Q(comment=main_comment)).order_by('timestamp')
	if(request.method=="POST"):
		ConvC.objects.create(
			comment=main_comment,
			user=request.user,
			text=request.POST.get('com'),
		)
	paginator = Paginator(conversation_list, 10)
	page = request.GET.get('page')
	try:
		conversations = paginator.page(page)
	except:
		conversations = paginator.page(1)
	
	return render(request, 'contests/convC.html', {'conversations':conversations, 'con':con, 'main':main_comment})