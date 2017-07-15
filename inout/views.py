from django.contrib.auth.models import User
from .forms import RegistrationForm, ActivateForm, CodeForm
from django.http import HttpResponse, JsonResponse		
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from inout.models import Profile
from contests.models import Contest, Problem, Solve
from django.core.mail import send_mail
from django.core import serializers
from django import forms
from subprocess import *
from .global_vars import *
import os, json
import random, socks, time


def is_activated(f):
	"""
	A decorator to allow only logged in and activated accounts to enter
	"""
	@login_required(login_url='/')
	def wrapper(*args, **kwargs):

		if(args[0].user.profile.activated):
			return f(*args, **kwargs)
		return redirect('inout:activate')

	return wrapper

def clogin(request):
	"""
	View for login page
	"""
	if request.user.is_authenticated():
		if(request.user.is_active):
			return redirect('inout:home')
		else:
			return redirect('inout:activate')
	else:
		return auth_views.LoginView.as_view(template_name='inout/login.html')(request)

def register(request):
	"""
	View for registration page
	"""
	form = RegistrationForm()
    
	if request.user.is_authenticated():
		return redirect('inout:home')
	
	elif request.method == 'POST':
		form = RegistrationForm(request.POST)
        
		if form.is_valid():
		
			u = User.objects.create_user(username = form.cleaned_data['username'],
										 password = form.cleaned_data['password1'],
										 first_name = form.cleaned_data['fname'],
										 last_name = form.cleaned_data['lname'],)
			code = ''
			for i in range(6):
				code += chr(random.randrange(48, 122))

			u.profile.birth = form.cleaned_data['dob']
			u.profile.activation_code = code
			print(code)
			u.profile.rating = 1200
			u.profile.save()

			"""
			send_mail('Activation Code',
					  f'This is your activation Code: {code}',
					  '<sender mail address>',
					  [list of all the recipients])
			Email the user
			"""
			usr = form.cleaned_data['username']
			form = ActivateForm(initial={})
			return redirect('inout:not_activated')
		else:
			return render(request, 'inout/register.html', {'form':form})
	else:
		return render(request, 'inout/register.html', {'form':form})
	
def activate(request):
	"""
	View to activate user's account.
	"""
	try:
		if not request.user.profile.activated:
			if request.method == 'POST':
				form = ActivateForm(request.POST)
				if form.is_valid():
					cd = request.user.profile.activation_code
					if(form.cleaned_data['act_code'] == cd):
						u = request.user
						u.profile.activated = True
						u.activation_code = ''
						u.profile.save()
						u.save()
						return redirect('/')
				error = 'Invalid Code, contact admin if you didn\'t get the code.'
				return render(request, 'inout/activate.html', {'form':form, 'error':error})
			else:
				return render(request, 'inout/activate.html', {'form':ActivateForm(initial={})})
		else:
			return redirect('/')

	except Exception as e:
		return redirect('inout:logout')
	

def not_activated(request):
	return render(request, 'inout/not_activated.html')


@is_activated
def index(request):
	"""
	Render home template
	"""
	return render(request, 'inout/home.html')

@is_activated
def give_contests(request):
	"""
	A view which provides contests which are requested to the moderator
	"""
	try:
		contests = Contest.objects.filter(allowed=0)
		if len(contests)==0:
			return JsonResponse({'status':'failure'}, status=200)
		contest_requests = serializers.serialize('json', contests)
		return HttpResponse(contest_requests, content_type='application/json')

	except Exception as e:
		return JsonResponse({'status':'failure'}, status=404)
	

@is_activated
def allow(request):
	"""
	The view to allow or reject a contest
	Only accessible by a staff or superuser.
	"""
	try:
		if(request.method == 'GET'):
			pp = int(request.GET.get('ag'))
			c = Contest.objects.get(pk=request.GET.get('pk'))
			if pp == 1:
				c.allowed = 1
				c.save()
				return JsonResponse({'done':'true'}, status=200)
			else:
				usr = c.admin
				usr.profile.tobecon = False
				usr.save()
				c.delete()
				return JsonResponse({'done':'true'}, status=200)
	except Exception as e:
		return JsonResponse({'done':'false'}, status=404)
	
	
@is_activated
def profile(request, username):
	"""
	Profile View, information about the user
	"""
	u = get_object_or_404(User, username=username)
	solved_list = Solve.objects.filter(user=u).order_by('-time')
	paginator=Paginator(solved_list, 10)
	page=request.GET.get('page')
	try:
		solved = paginator.page(page)
	except:
		solved = paginator.page(1)
	return render(request, 'inout/profile.html', {'user':u, 'solved':solved})


def is_alright(string, lang):
	"""
	Heuristic check of some malicious intentions of user in code
	
	"""
	string = string.lower()
	
	if 'python' in lang:
		if 'system(' in string or 'popen' in string:
			return False
		else:
			return True
	elif lang == 'java':
		if '.getruntime(' in string or 'processbuilder(' in string:
			return False
		else:
			return True
	elif 'subprocess' in string:
		return False
	return True

@is_activated
def code_edit(request):
	"""
	Code, Compile and run
	"""
	form = CodeForm(initial={})
	if request.method == 'POST':
        
		form = CodeForm(request.POST)
		
		lang = request.POST.get('language')
		code = request.POST.get('code')
		if not is_alright(code, lang):
			return HttpResponse('Invalid Code')
        
		code_path = os.path.join(os.getcwd(), f'tmp/{request.user.username}/code{extensions[lang]}')
		input_file = os.path.join(os.getcwd(), f'tmp/{request.user.username}/inp.txt')
        
		with open(code_path, 'w') as file:
			file.write(request.POST.get('code'))
		
		with open(input_file, 'w') as file:
			file.write(request.POST.get('inpt'))
		
		if 'python' in lang:
			run_cmd = 'timeout 5s {}'.format(cmd[lang][1]%(code_path, input_file))
			try:
				ps = check_output(run_cmd, shell=True, stderr=STDOUT).decode('utf-8')
				return HttpResponse(ps)
			except CalledProcessError as e:
				if("status 124" not in str(e)):
					retdata = "<pre>{}</pre>".format("<br>".join(e.output.decode('utf-8').split("\n")))
					return HttpResponse(retdata)
				elif("status 1" in str(e)):
					return HttpResponse("Time Exceeded: 5.0s")
				else:
					return HttpResponse("Server Error")
		else:
			outpt = "a.out" if lang != "java" else '';
			output_path = os.path.join(os.getcwd(), 'tmp/{}/{}'.format(request.user.username, outpt))
			
			if lang !='java':
				compile_cmd = cmd[lang][0]%(code_path, output_path)
			else:
				compile_cmd = f'javac tmp/{request.user.username}/code.java'

			try:
				ps = check_output(compile_cmd, shell=True, stderr=STDOUT).decode('utf-8')

				if lang!='java':
					run_cmd = "timeout 5s "+((cmd[lang][1]%(output_path, input_file)))

				else:
					run_cmd = "java -cp %s < %s"%(os.path.join(os.getcwd(),"tmp/%s Main"%request.user.username), input_file)

				ps = check_output(run_cmd, shell=True, stderr=STDOUT).decode('utf-8')
				return HttpResponse(ps)

			except CalledProcessError as e:
				retdata = "<pre>{}</pre>".format("<br>".join(e.output.decode('utf-8').split("\n")))
				return HttpResponse(retdata)

	else: return render(request, 'inout/code-edit.html', {'form':form})




