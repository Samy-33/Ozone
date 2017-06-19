
from .forms import *
from django.http import HttpResponse, JsonResponse		
from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required#, csrf.csrf_protect
from inout.models import Profile
from contests.models import Contest, Problem
import random, socks, time
from django.core.mail import send_mail
import os, json
from subprocess import *


extensions = {
	'cpp':".cpp",
	'c':'.c',
	'python2':'.py',
	'python3':'.py',
	'java':'.java',
}

cmd = {
	'cpp':("g++ %s -o %s", "./%s < %s"),
	'c':("gcc %s -o %s", "./%s < %s"),
	'python2':('python %s < %s', 'python %s < %s'),
	'python3':('python3 %s < %s','python3 %s < %s'),
	'java':('javac %s', 'java %s < %s'),
}


#def compile(request, filename)


#from django.contrib.auth.models improt Users
# Create your views here.

#def login(request):
#	if request.user.is_authenticated:
#		return render(request, "inout/home.html")
#	#else: return auth_views.login(request)
#	#auth_views.login(request, {'template_name':'inout/login.html'})



def clogin(request):
	if request.user.is_authenticated():
		if(request.user.is_active):
			return redirect("/home/")
		else:
			return redirect("/activate/")
	else:
		return auth_views.login(request, "inout/login.html")

#@csrf.csrf_protect
def register(request):
	form = RegistrationForm()
	if request.user.is_authenticated():
		return redirect('/home/')
	elif request.method == 'POST':
		form = RegistrationForm(request.POST)
		if form.is_valid():
			u = User.objects.create_user(
				username = form.cleaned_data['username'],
				password = form.cleaned_data['password1'],
				is_active = False,
				first_name = form.cleaned_data['fname'],
				last_name = form.cleaned_data['lname'],
			)
			u.save()
			code = ""
			for i in range(6):
				code += chr(random.randrange(48, 122))
			p = Profile.objects.get(user=u)
			p.hd = form.cleaned_data['hd']
			p.birth = form.cleaned_data['dob']
			p.activation_code = code
			p.rating = 1500
			#p = Profile.objects.create(user=u, hd=form.cleaned_data['hd'], birth=form.cleaned_data['dob'], activation_code=code, rating=1500)
			p.save()
#			u.save()
#			send_mail("Activation Code", "This is your activation Code: %s"%code, 'saket.patel@iiitdmj.ac.in', ['saket.is.sam@gmail.com'])
			##Email the user
			hdd = form.cleaned_data['hd']
			usr = form.cleaned_data['username']
			form = ActivateForm(initial={})
			return render(request, 'inout/activate.html', {'uuuuu':hdd, 'usr':usr, 'form':form})
		else:
			return render(request, 'inout/register.html', {'form':form})
	else:
		return render(request, 'inout/register.html', {'form':form})
	

#@login_required(login_url="/")
def activate(request):
	form = None
	try:
		if(request.method == "POST"):
			form = ActivateForm(request.POST)
			if(not request.user.is_active):
				if form.is_valid():
					print(form.cleaned_data['act_code'])
					print(Profile.objects.get(hd=request.POST.get('hdd')).activation_code)
					if(form.cleaned_data['act_code'] == Profile.objects.get(hd=request.POST.get('hdd')).activation_code):
						#p = Profile.objects.get(user=request.user)
						u = User.objects.get(username=request.POST.get('usr'))
						u.is_active = True
						u.activation_code = ""
						u.save()
						st = "tmp/%s"%(request.POST.get('usr'))
#						print(st)
						os.mkdir(st)
						return redirect('/')
				return render(request, 'inout/activate.html', {'form':form})
			else:
				return redirect('/')
		else:
			return redirect('/')
	except:
		return redirect('/')
	
	
@login_required(login_url="/")
def index(request):
	return render(request, "inout/home.html")

@login_required(login_url='/')
def give_contests(request):
	try:
		contest_requests = Contest.objects.get(allowed=0)
		return JsonResponse(contest_requests, safe=False)
#		return JsonResponse(contest_requests, safe=False, status=200)
	except:
		return JsonResponse({'status':'failure'}, status=404)
	

@login_required(login_url='/')
def profile(request):
	return render(request, "inout/profile.html")

@login_required(login_url='/')
def code_edit(request):
	form = CodeForm(initial={})
	if request.method == 'POST':
		form = CodeForm(request.POST)
		
		#fil = str(request.POST.get('code'))
		print(str(request.POST.get('inpt')))
		lng = str(request.POST.get('language'))
		ext = extensions[lng]
		directory = "tmp/%s"%(request.user.username)
		filename="%s/fil%s"%(directory, ext)
		inp = "%s/in"%(directory)
		with open(filename, "w") as fil:
#			fil.write("#!/usr/bin/env python\n")
			fil.write(str(request.POST.get('code')))
		if('python' not in lng):
			try:
				check_output(cmd[lng][0]%(filename, "%s/a.out"%(directory)), shell=True, stderr=STDOUT)
				os.system("chmod u+rx %s"%filename)
#				os.system("chmod u+x ")
			except CalledProcessError as e:
				e = e.output.split("\n")
				e = "<br>".join(e)
				e = e.split(" ")
				e = "&nbsp".join(e)
				os.system("rm %s"%(filename))
				return HttpResponse("<pre>%s</pre>"%e)
			try:
				#Change here so that file runs on each testcase (loop)
				with open(inp, "w") as fil:
					fil.write(str(request.POST.get('inpt')))
				p=check_output(cmd[lng][1]%("%s/a.out"%(directory), inp), shell=True, stderr=STDOUT)
				os.system("rm %s"%filename)
				os.system("rm %s"%(inp))
				os.system("rm %s"%(directory+"/a.out"))
			except CalledProcessError as e:
				e = e.output
				return HttpResponse("<pre>%s</pre>"%e)
			else:
				return HttpResponse("<pre>%s</pre>"%p)
		else:
			try:
				#Change here so that file runs on each testcase (loop)
				with open(inp, "w") as fil:
#					print(directory+"/in")
					fil.write(str(request.POST.get('inpt')))
				p = check_output(cmd[lng][0]%(filename, inp), shell=True, stderr=STDOUT)
				os.system("rm %s"%(inp))
				os.system("rm %s"%filename)
			except CalledProcessError as e:
				e = e.output.split("\n")
				e = "<br>".join(e)
				e = e.split(" ")
				e = "&nbsp".join(e)
				return HttpResponse("<pre>%s</pre>"%e)
			else:
				return HttpResponse("<pre>%s</pre>"%p)

	else: return render(request, 'inout/code-edit.html', {'form':form})




