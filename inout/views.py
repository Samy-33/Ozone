import os
import json
import random
import socks
import time
from subprocess import *

from django import forms
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.template import loader

from contests.models import Contest, Problem, Solve, CommentC, CommentQ, Ranking
from .global_vars import *
from .models import Profile
from .decorators import is_activated
from .forms import RegistrationForm, ActivateForm, CodeForm
from .helpers import issue_new_csrf_token

INVALID_ACTIVATION_CODE = 'Invalid Code, contact admin if you didn\'t get the code.'


@require_http_methods(['GET'])
def clogin(request):
    """
    View for authentication page
    """

    hide_section_states = { 'login': True, 'register': True, 'activate': True }
    show_section = request.GET.get('showSection', '')

    if show_section and show_section in hide_section_states.keys():
        hide_section_states[show_section] = False
    else:
        hide_section_states['login'] = False
        hide_section_states['register'], hide_section_states['activate'] = True, True

    if request.user.is_authenticated():
        if request.user.profile.activated:
            return redirect('inout:home')
        else:
            hide_section_states['activate'] = False
            hide_section_states['login'], hide_section_states['register'] = True, True
    elif show_section == 'activate':
        hide_section_states['activate'], hide_section_states['login'] = True, False


    register_form = RegistrationForm()
    activate_form = ActivateForm(initial={})

    context = {
        'register_form': register_form,
        'activate_form': activate_form,
        'hide_login': hide_section_states['login'],
        'hide_register': hide_section_states['register'],
        'hide_activate': hide_section_states['activate']
    }

    return render(request, 'inout/auth.html', context)


@require_http_methods(['POST'])
def authenticate_user(request):
    """
    View for authenticating a user
    """

    resp = { 'success': False, 'message': ['GET method not allowerd'] }

    if request.is_ajax():
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        user = authenticate(username=username, password=password)

        if user is not None:
            is_activated = user.profile.activated
            login(request, user)

            if not is_activated:
                request = issue_new_csrf_token(request)

            resp = { 'success': True, 'is_activated': is_activated }
        else:
            resp = { 'success': False, 'message': ['Enter a valid username/password.'] }

    return HttpResponse(json.dumps(resp), content_type='application/json')


@require_http_methods(['POST'])
def register(request):
    """
    View for registration page
    """

    resp = { 'success': False, 'message': ['GET method not allowerd'] }
    form = RegistrationForm()

    if request.is_ajax():
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = User.objects.create_user(
                username = form.cleaned_data['username'],
                password = form.cleaned_data['password1'],
                first_name = form.cleaned_data['fname'],
                last_name = form.cleaned_data['lname'],
            )

            code = ''.join([chr(random.randrange(48, 122)) for i in range(6)])

            user.profile.birth = form.cleaned_data['dob']
            user.profile.activation_code = code

            print(code)

            user.profile.rating = 1200
            user.profile.save()

            login(request, user)

            request = issue_new_csrf_token(request)

            """
            send_mail('Activation Code',
                      f'This is your activation Code: {code}',
                      '<sender mail address>',
                      [list of all the recipients])
            Email the user
            """

            resp = { 'success': True }
        else:
            error_json = json.loads(form.errors.as_json())
            codes = [error_json[error][0]['code'] for error in error_json]
            messages = [error_json[error][0]['message'] for error in error_json]

            if 'required' in codes:
                messages = ['Required fields are absent.']

            resp = { 'success': False, 'message': messages }

    return HttpResponse(json.dumps(resp), content_type='application/json')


@require_http_methods(['POST'])
def activate(request):
    """
    View to activate user's account.
    """

    try:
        if not request.user.profile.activated:
            if request.method == 'POST':
                form = ActivateForm(request.POST)

                if form.is_valid():
                    activation_code = request.user.profile.activation_code
                    if form.cleaned_data['act_code'] == activation_code:
                        user = request.user
                        user.profile.activated = True
                        user.activation_code = ''
                        user.profile.save()
                        user.save()

                        return redirect('/')

                messages.add_message(request, messages.ERROR, INVALID_ACTIVATION_CODE)
                return redirect('/?showSection=activate')
        else:
            return redirect('/')

    except Exception as e:
        return redirect('inout:logout')


@is_activated
def index(request):
    """
    Render home template
    """

    convc = CommentC.objects.all().order_by('-timestamp')[:10]
    convq = CommentQ.objects.all().order_by('-timestamp')[:10]

    return render(request, 'inout/home.html', {'convc':convc, 'convq':convq})

@is_activated
def give_contests(request):
    """
    Returns html code containing contest requests
    """

    if request.is_ajax() and (request.user.is_staff or request.user.is_superuser):
        contests = Contest.objects.filter(allowed=0)
        contest_request_template = loader.get_template('inout/contest_requests.html')
        contest_requests_html = contest_request_template.render({ 'contests': contests })
        resp = { 'contest_requests_html': contest_requests_html }
    else:
        resp = { 'success': False, 'message': 'Only XMLHttp request allowed by staff/superusers' }

    return HttpResponse(json.dumps(resp), content_type='application/json')


@csrf_exempt
@is_activated
def allow(request):
    """
    The view to allow or reject a contest
    Only accessible by a staff or superuser.
    """

    if request.is_ajax() and (request.user.is_staff or request.user.is_superuser):
        is_allowed = int(request.POST.get('is_allowed', -1))
        contest_code = request.POST.get('contest_code', None)

        if is_allowed not in [1, 0] or contest_code is None:
            resp = { 'success': False, 'message': 'Invalid post parameters' }

        else:
            contest = Contest.objects.get(contest_code=contest_code)

            if is_allowed == 1:
                contest.allowed = 1
                contest.save()

            elif is_allowed == 0:
                user = contest.admin
                user.profile.tobecon = False
                user.save()
                contest.delete()

            resp = { 'success': True }
    else:
        resp = { 'success': False, 'message': 'Only XMLHttp request allowed by staff/superusers' }

    return HttpResponse(json.dumps(resp), content_type='application/json')


@is_activated
def profile(request, username):
    """
    Profile View, information about the user
    """

    user = get_object_or_404(User, username=username)
    solved_problems_qs = Solve.objects.filter(user=user).order_by('-time')

    paginator = Paginator(solved_problems_qs, 10)
    page = request.GET.get('page', 1)
    solved_problems = paginator.page(page)

    return render(request, 'inout/profile.html', { 'user': user, 'solved_problems': solved_problems })


def is_alright(string, lang):
    """
    Heuristic check of some malicious intentions of user in code
    """
    string = string.lower()

    if 'python' in lang:
        if 'import os' in string or 'system(' in string or 'popen' in string:
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

"""
This area is to calculate new rating after the contest
"""

def expect(user_rating, opp_rating):
    return 1/(1+10**((opp_rating-user_rating)*400))

def calculate_rating(old_rating, expected_rating, actual_rating, k_factor):
    return old_rating + k_factor*(actual_rating-expected_rating)


@is_activated
def update(request, contest):
    contest = get_object_or_404(Contest, contest_code=contest)
    if contest.updated or not contest.rated:
        return JsonResponse({'status':'IC', 'error':'invalid contest'}, status=200)
    users = Ranking.objects.filter(contest=contest)
    users = sorted(users, key=lambda t:(-t.effective_score, t.penalty))
    expected = {}
    actual = {}
    new_rating = {}
    for i, user in enumerate(users):
        expected[user.user] = 0
        actual[user.user] = 0
        for j, user2 in enumerate(users):
            if i == j:
                continue
            expected[user.user] += expect(user.user.profile.rating, user2.user.profile.rating)
            actual[user.user] += 0 if i > j else 1

        new_rating[user.user] = calculate_rating(user.user.profile.rating,
                                                 expected[user.user],
                                                 actual[user.user], 30)

    for user in new_rating:
        user.profile.rating = new_rating[user]
        user.profile.save()
        user.save()

    contest.admin.profile.tobecon = False
    contest.admin.profile.save()
    contest.admin.save()
    contest.updated = True
    contest.save()
    return JsonResponse({'status':'SC', 'error':'No Error'}, status=200)

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

        from ozone.settings import CODEDIR
        code_path = os.path.join(CODEDIR, f'tmp/{request.user.username}/code{extensions[lang]}')
        input_file = os.path.join(CODEDIR, f'tmp/{request.user.username}/inp.txt')

        with open(code_path, 'w+') as file:
            file.write(request.POST.get('code'))

        with open(input_file, 'w+') as file:
            file.write(request.POST.get('inpt'))

        if 'python' in lang:
            run_cmd = 'timeout 5s {}'.format(cmd[lang][1]%(code_path, input_file))
            print(cmd[lang])
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
                compile_cmd = f'javac {CODEDIR}/tmp/{request.user.username}/code.java'

            try:
                ps = check_output(compile_cmd, shell=True, stderr=STDOUT).decode('utf-8')

                if lang != 'java':
                    run_cmd = "timeout 5s "+((cmd[lang][1]%(output_path, input_file)))

                else:
                    run_cmd = "java -cp %s < %s"%(os.path.join(CODEDIR,"tmp/%s Main"%request.user.username), input_file)

                ps = check_output(run_cmd, shell=True, stderr=STDOUT).decode('utf-8')
                return HttpResponse(ps)

            except CalledProcessError as e:
                retdata = "<pre>{}</pre>".format("<br>".join(e.output.decode('utf-8').split("\n")))
                return HttpResponse(retdata)

    else: return render(request, 'inout/code-edit.html', {'form':form})


@is_activated
def feedback(request):
    pass
