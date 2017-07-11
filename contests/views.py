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
from inout.global_vars import (extensions, cmds, output)
from .forms import (CreateContest, Prob, EditProb)
from inout.global_func import aware
from inout.views import is_activated
from time import sleep
import datetime
import pytz
import subprocess as sb


@is_activated
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
	try:
		past_contests = Contest.objects.filter(Q(end_date__lt=aware(datetime.datetime.now())))
	except:
		past_contests = []
	return render(request, 'contests/contests.html', {'upcoming':upcoming, 'current':current,
													  'usrs_contest':usrs_contest, 'past_contests':past_contests})


@is_activated
def create(request):

	if request.method == 'POST':

		form = CreateContest(request.POST)
	
		if form.is_valid():
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
			return redirect('contests:contest', code=c.contest_code)
		else:
			return render(request, 'contests/create_contest.html', {'form':form, 'done':False})
	else:
		form = CreateContest(initial={})
		return render(request, 'contests/create_contest.html', {'form':form, 'done':False})


@is_activated
def contest(request, code):
	con = get_object_or_404(Contest, Q(contest_code=code))

	dt = aware(datetime.datetime.now())-con.start_date
	if dt.days < 0 or dt.seconds < 0:
		pp = True
	else:
		pp = False
	return render(request, 'contests/contest.html', {'contest':con, 'pp':pp})


@is_activated
def editc(request, code):
	con = get_object_or_404(Contest, Q(contest_code=code)&Q(end_date__gte=datetime.datetime.now()))

	if con.admin == request.user:
		if con.end_date >= aware(datetime.datetime.now()):
			aled = True
		else:
			aled = False

		return render(request, 'contests/editc.html', {'contest':con, 'aled':aled})

	return render(request, 'contests/editc.html', {'contest':False})


@is_activated
def editq(request, code, question):
	contest = get_object_or_404(Contest, contest_code=code)
	problem = get_object_or_404(Problem, code=question)
	if request.method=='POST':
		form = EditProb(request.POST)
		if form.is_valid():
			problem.name = form.cleaned_data['name']
			problem.n_testfiles = form.cleaned_data['n_testfiles']
			problem.time_lim = form.cleaned_data['time_lim']
			problem.text = form.cleaned_data['text']
			problem.score = form.cleaned_data['score']
			problem.save()
			import os, shutil
			present_directory = os.getcwd()
			path_to_edit = os.path.join(present_directory, f'tmp/problems/{problem.code}')
			shutil.rmtree(path_to_edit)
			os.makedirs(path_to_edit)

			for file in request.FILES:
				with open(os.path.join(path_to_edit, file), 'w') as f:
					for line in request.FILES[file].readlines():
						f.write(line.decode('utf-8'))
			return redirect('contests:editc', code=code)
			
		else:
			return render(requset, 'contests/editq.html', {'form':form})
		pass
	form = EditProb({'name': problem.name,
				    'n_testfiles': problem.n_testfiles,
					'time_lim': problem.time_lim,
					'score': problem.score,
					'text': problem.text
					})
	return render(request, 'contests/editq.html', {'form':form})


@is_activated
def problem(request, code, question):
	con = get_object_or_404(Contest, contest_code=code)
	ques = get_object_or_404(Problem, code=question)
	return render(request, 'contests/problem.html', {'contest':con, 'ques':ques})


@is_activated
def addq(request, code):
	if(request.method=='POST'):
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
				present_directory = os.getcwd()
				path = os.path.join(present_directory, f'tmp/problems/{pb.code}')
				os.makedirs(path)
				
				for file in request.FILES:
					with open(os.path.join(path, file), "w") as f:
						for line in request.FILES[file].readlines():
							f.write(line.decode('utf-8'))
				
				return redirect('contests:editc', code=code)
			else:
				return render(request, 'contests/addq.html', {'form':form})

		except Exception as e:
			return render(request, 'contests/addq.html', {'form':Prob(initial={})})

	return render(request, 'contests/addq.html', {'form':Prob(initial={})})

"""
## This whole region is for checking the user's output agains the given test outputs

"""


@csrf_protect
@is_activated
def submit(request, code):
	if request.method == 'POST':
		
		from inout.views import is_alright
		
		if not is_alright(request.POST.get('code'), request.POST.get('lang')):
			return JsonResponse({'status':'Code execution failure', 'Error':'Invalid Code.'})
		
		maximum_time_taken = 0.0
		
		q = get_object_or_404(Problem, code=code)
		
		import os
		
		path_for_problem = os.path.join(os.getcwd(), f'tmp/{request.user.username}/{code}')
		
		if not os.path.exists(path_for_problem):
			os.makedirs(path_for_problem)
		
		path_for_tests = os.path.join(os.getcwd(), f'tmp/problems/{code}')
		codepath = os.path.join(path_for_problem, 'code{}'.format(extensions[request.POST.get('lang')]))
		outputpath = os.path.join(path_for_problem, output[request.POST.get('lang')])

		with open(codepath, 'w') as file:
			file.write(request.POST.get('code'))

		"""
		## This is compiling the code
		"""
		if 'python' not in request.POST.get('lang'):
			try:
				compile_cmd = cmds[request.POST.get('lang')][0]%(codepath, outputpath) if request.POST.get('lang') !='java' else f'javac tmp/{request.user.username}/{q.code}/code.java'
				## Not secure
				sb.check_output(compile_cmd.strip(), shell=True, stderr=sb.STDOUT).decode('utf-8')

			except sb.CalledProcessError as e:
				removeDir(request, code)
				if 'status 124' not in str(e):
					retdata = "<pre>{}</pre>".format("<br>".join(e.output.decode('utf-8').split('\n')))
					return JsonResponse({'status':'compile_error', 'error':retdata})
				return JsonResponse({'status':'SE', 'error':'Unknow System Error, contact admin.'})
		"""
		## Ending the compilation process If successful, move on to run the code and output
		"""

		for i in range(q.n_testfiles):
			## Separate Code for Python
			if 'python' in request.POST.get('lang'):
				run_cmd = "timeout "+str(q.time_lim)+"s time "+(cmds[request.POST.get('lang')][1]%(codepath,
																								  os.path.join(path_for_tests, f'in{i}.txt'),
																								   os.path.join(path_for_problem, f'uout{i}.txt')))
				try:
					res = sb.check_output(run_cmd.strip(), shell=True, stderr=sb.STDOUT).decode('utf-8')
					retcode = check(request.user, q.code, i)
					if(retcode==1):

						current_time_taken = float(res.split()[2].split('e')[0].split(":")[1])
						maximum_time_taken = max(maximum_time_taken, current_time_taken)

					elif retcode==0:
						removeDir(request, code)
						if (not already(request.user, q)) and q.contest.start_date<=aware(datetime.datetime.now()) and q.contest.admin != request.user:
							addWA(request, q)
						return JsonResponse({'status':'WA', 'error':f'WA in testcase {i+1}'})
					else:
						removeDir(request, code)
						if (not already(request.user, q)) and q.contest.end_date>aware(datetime.datetime.now()) and q.contest.admin != request.user:
							addWA(request, q)

						return JsonResponse({'status':'SE', 'error':f'Results can\'t be matched properly'})
				except sb.CalledProcessError as e:
					
					removeDir(request, code)
					if "status 124" not in str(e):
						retdata = "<pre>%s</pre>"%("<br>".join(e.output.decode('utf-8').split('\n')))
						return JsonResponse({'status':'compile_error', 'error':retdata})
					if (not already(request.user, q)) and q.contest.end_date>aware(datetime.datetime.now()) and q.contest.admin != request.user:
						addWA(request, q)
					return JsonResponse({'status':'TLE', 'error':'Time Limit Exceeded'})
			else:
				try:
					if request.POST.get('lang') == 'java':
						outputpath = f'tmp/{request.user.username}/{q.code} Main'
					run_cmd = "timeout "+str(q.time_lim)+"s time "+(cmds[request.POST.get('lang')][1]%(outputpath,
																									  os.path.join(path_for_tests, 'in%d.txt'%i),
																									  os.path.join(path_for_problem, 'uout%d.txt'%i)))
					### Not Secure
					res = sb.check_output(run_cmd.strip(), shell=True, stderr=sb.STDOUT).decode('utf-8')
					
					retcode = check(request.user, q.code, i)
					if retcode==1:
						current_time_taken = float(res.split()[2].split('e')[0].split(":")[1])
						maximum_time_taken = max(maximum_time_taken, current_time_taken)
						
					elif retcode==0:
						removeDir(request, code)
						if (not already(request.user, q)) and q.contest.end_date>aware(datetime.datetime.now()) and q.contest.admin != request.user:
							addWA(request, q)
						return JsonResponse({'status':'WA', 'error':f'WA in testcase {i+1}'})
					else:
						removeDir(request, code)
						return JsonResponse({'status':'SE', 'error':'Results can\'t be matched properly. Contact Admin.'})

				except sb.CalledProcessError as e:
					if 'status 124' in str(e):
						removeDir(request, code)
						if (not already(request.user, q)) and q.contest.end_date>saware(datetime.datetime.now()) and q.contest.admin != request.user:
							addWA(request, q)
						return JsonResponse({'status':'TLE', 'error':f'TLE {q.time_lim+0.1}'})
					if 'status 1' in str(e):
						removeDir(request, code)
						return JsonResponse({'status':'RTE', 'error':'Run Time Error'})
		removeDir(request, code)
		if (not already(request.user, q)) and q.contest.end_date>aware(datetime.datetime.now()) and q.contest.admin != request.user:
			addAC(request, q)
		if not already(request.user, q):
			addSolve(request, q)
		return JsonResponse({'status':'Accepted', 'error':f'Time Taken: {maximum_time_taken}'})

	return  JsonResponse({'status':'No testcases', 'error':'can\'t find any testcase for this problem'})


def removeDir(request, code):
	import os, shutil
	path_to_clear = os.path.join(os.getcwd(), f'tmp/{request.user.username}/{code}')
	if(os.path.exists(path_to_clear)):
		shutil.rmtree(path_to_clear)
	
	
def check(user, problem, n):
	try:
		import os
		user_output = open(os.path.join(os.getcwd(), f'tmp/{user}/{problem}/uout{n}.txt'), 'r')
		exp_output = open(os.path.join(os.getcwd(), f'tmp/problems/{problem}/out{n}.txt'), 'r')
		user_line, expected_line = '1', '1'
		while user_line != '' or expected_line != '':
			user_line = user_output.readline().strip()
			expected_line = exp_output.readline().strip()
			if user_line != expected_line:
				return 0
		return 1
	except Exception as e:
		return 2
		
def already(user, q):
	return Solve.objects.filter(Q(problem=q)&Q(user=user)).exists()

def addSolve(request, q):
	Solve.objects.create(user=request.user, problem=q)

def addAC(request, q):
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
		p.wa += 1
		p.save()
	except:
		p = Ranking.objects.create(user=request.user, contest=q.contest)
		p.wa = 1
		p.save()
"""

## Here is the end of Submission check view and related functions

"""

@is_activated
def deleteq(request, code):
	q = get_object_or_404(Problem, code=code)
	
	if q.contest.admin == request.user:
		q.delete()
		import os
		try:
			import shutil
			shutil.rmtree(f'./tmp/problems/{code}')
		except:
			pass
	else:
		raise Http404
	return HttpResponse("Done")


@is_activated
def rankings(request, contest):
	con = get_object_or_404(Contest, contest_code=contest)
	if(con.start_date <= aware(datetime.datetime.now())):
		data = sorted(Ranking.objects.filter(Q(contest=con)), key=lambda t:-t.effective_score)
		return render(request, 'contests/ranking.html', {'con':data, 'contest':con})
	else:
		return render(request, 'contests/ranking.html', {'con':[], 'contest':con})

	

@is_activated
def deletec(request, contest):
	con = get_object_or_404(Contest, contest_code=contest)
	
	if con.start_date >= aware(datetime.datetime.now()):
		request.user.profile.tobecon = False
		request.user.profile.save()
		import os, shutil
		for problem in con.problem_set.all():
			path_to_remove = os.path.join(os.getcwd(), f'tmp/problems/{problem.code}')
			if os.path.exists(path_to_remove):
				shutil.rmtree(path_to_remove)
		con.delete()
		return JsonResponse({'done':'Yes, Did that.'}, status=200)
	return JsonResponse({'done':'Nope cant do that'}, status=200)


@is_activated
def boardC(request, contest):
	con = get_object_or_404(Contest, contest_code=contest)
	if request.method=='POST':
		CommentC.objects.create(
			contest=con,
			user=request.user,
			text = request.POST.get('com'),
		)
	comments_list = CommentC.objects.filter(Q(contest=con)).order_by('-timestamp')
	paginator = Paginator(comments_list, 10)
	page = request.GET.get('page')
	try:
		comments = paginator.page(page)
	except:
		comments = paginator.page(1)
	
	return render(request, 'contests/discussionC.html', {'comments':comments, 'con':con})
	
	
@is_activated
def boardQ(request, code):
	prob = get_object_or_404(Problem, code=code)
	if request.method=='POST':
		CommentQ.objects.create(
			problem=prob,
			user=request.user,
			text = request.POST.get('com'),
		)
	comments_list = CommentQ.objects.filter(Q(problem=prob)).order_by('-timestamp')
	paginator = Paginator(comments_list, 10)
	page = request.GET.get('page')
	try:
		comments = paginator.page(page)
	except:
		comments = paginator.page(1)
		
	return render(request, 'contests/discussionQ.html', {'comments':comments, 'prob':prob})


@is_activated
def convQ(request, question, pk):
	main_comment = get_object_or_404(CommentQ, id=pk)
	prob = get_object_or_404(Problem, code=question)
	conversation_list = ConvQ.objects.filter(Q(comment=main_comment)).order_by('timestamp')
	if request.method=='POST':
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


@is_activated
def convC(request, code, pk):
	main_comment = get_object_or_404(CommentC, id=pk)
	con = get_object_or_404(Contest, contest_code=code)
	conversation_list = ConvC.objects.filter(Q(comment=main_comment)).order_by('timestamp')
	if request.method=='POST':
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