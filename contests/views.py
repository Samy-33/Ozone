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
                     ConvC, ConvQ,)
from practice.models import Tag, ProblemTag
from inout.global_vars import (extensions, cmds, output)
from .forms import (CreateContest, Prob, EditProb)
from inout.global_func import aware
from inout.views import is_activated
from time import sleep
import datetime
import pytz
import subprocess as sb

from ozone.settings import CODEDIR


@is_activated
def index(request):
    """
    Main view for contests page
    : Shows all the present, past, ccurrent and user's contests
    """

    upcoming = Contest.objects.filter(Q(start_date__gt=datetime.datetime.now())
                                      &Q(allowed=1)).order_by('-start_date')

    current = Contest.objects.filter(Q(start_date__lte=datetime.datetime.now())
                                     &Q(end_date__gt=datetime.datetime.now())
                                     &Q(allowed=1)).order_by('-start_date')

    usrs_contest = Contest.objects.filter(Q(admin=request.user))

    past_contests = Contest.objects.filter(Q(end_date__lt=aware(datetime.datetime.now())))

    return render(request, 'contests/contests.html', {'upcoming':upcoming, 'current':current,
                                                      'usrs_contest':usrs_contest,
                                                      'past_contests':past_contests})


@is_activated
def create(request):
    """
    This view is to create a contest
    : No user can have more than one contests upcoming or ongoing.
    : Moderator needs to allow or reject contest
    variables:
    # c: Contest variable which is created
    """
    if request.method == 'POST':

        form = CreateContest(request.POST)

        if form.is_valid():

            c = Contest.objects.create(
                admin = request.user,
                name = form.cleaned_data['name'],
                contest_code=form.cleaned_data['contest_code'],
                start_date=form.cleaned_data['start_date'],
                end_date=form.cleaned_data['end_date'],
                allowed=0,)

            request.user.profile.tobecon = True
            request.user.save()

            return redirect('contests:contest', contest=c.contest_code)
        else:
            return render(request, 'contests/create_contest.html', {'form':form, 'done':False})
    else:
        form = CreateContest(initial={})
        return render(request, 'contests/create_contest.html', {'form':form, 'done':False})


@is_activated
def contest(request, contest):
    """
    View which provides the main view of a particular contest
    Variables
    # con: contest asked
    # dt: difference between current time and start time of contest
    # pp: if contest has passed or not.
    """
    con = get_object_or_404(Contest, Q(contest_code=contest))

    dt = aware(datetime.datetime.now())-con.start_date
    if dt.days < 0 or dt.seconds < 0:
        pp = True
    else:
        pp = False
    return render(request, 'contests/contest.html', {'contest':con, 'pp':pp})


@is_activated
def editc(request, contest):
    """
    This view is to edit a particular contest
    Variables
    # contest: Contest to be edited
    # allow_edit: Allow edit if allow_edit is True means allow only if contest
                  is ongoing or upcoming
    """
    contest = get_object_or_404(Contest, Q(contest_code=contest)
                            &Q(end_date__gte=datetime.datetime.now()))
    if contest.admin == request.user:
        if contest.end_date >= aware(datetime.datetime.now()):
            allow_edit = True
        else:
            allow_edit = False

        return render(request, 'contests/editc.html', {'contest':contest, 'aled':allow_edit})

    return render(request, 'contests/editc.html', {'contest':False})


def create_test_files(request, problem, edit_problem=False):
    import os
    present_directory = CODEDIR
    path = os.path.join(present_directory, f'tmp/problems/{problem.code}')
    if edit_problem:
        import shutil
        shutil.rmtree(path)
    os.makedirs(path)

    """
    Create input and output data files in problem directory
    """
    for file in request.FILES:
        with open(os.path.join(path, file), "w") as f:
            for line in request.FILES[file].readlines():
                f.write(line.decode('utf-8'))

def create_tag_problems(form, problem):
    tags = form.cleaned_data['tags']
    for tag_id in tags:
        try:
            tag = Tag.objects.get(id=tag_id)
            print(tag)
            ProblemTag.objects.create(
                tag = tag,
                problem = problem,
            )
        except Exception as e:
            print(e.decode('utf-8'))

@is_activated
def addq(request, contest):
    """
    View to add a new question to a particular contest
    Variables
    # con: contest in which question is to be added
    # pb: This is the question sent as the POST data
    """
    if(request.method=='POST'):
        try:
            con = Contest.objects.get(contest_code=contest)
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

                create_test_files(request, pb)
                create_tag_problems(form, pb)

                return redirect('contests:editc', contest=contest)
            else:
                return render(request, 'contests/addq.html', {'form':form})

        except Exception as e:
            return render(request, 'contests/addq.html', {'form':Prob(initial={})})

    return render(request, 'contests/addq.html', {'form':Prob(initial={})})


@is_activated
def editq(request, contest, question):
    """
    This view is to allow editing of a problem
    Variables
    # contest: Contest in which the problem belongs
    # problem: The problem which is to be edited
    """
    contest = get_object_or_404(Contest, contest_code=contest)
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

            """
            Add newly added test data to the problem directory
            """
            create_test_files(request, problem, edit_problem=True)

            return redirect('contests:editc', contest=contest)

        else:
            context = {
                'form': form,
                'con_code': contest.contest_code,
                'q_code': problem.code
            }
            return render(requset, 'contests/editq.html', context)

    form = EditProb({'name': problem.name,
                     'n_testfiles': problem.n_testfiles,
                     'time_lim': problem.time_lim,
                     'score': problem.score,
                     'text': problem.text})
    return render(request, 'contests/editq.html', {'form':form,
                                                   'con_code':contest.contest_code,
                                                   'q_code':problem.code})


@is_activated
def problem(request, contest, question):
    """
    This view is to show data about a particular problem and allow submission
    Variables
    # con: Contest in which problem belongs
    # ques: The problem
    """
    contest = get_object_or_404(Contest, contest_code=contest)
    if contest.start_date > aware(datetime.datetime.now()) and request.user != contest.admin:
        return redirect('contests:contest', contest=contest.contest_code)
    problem = get_object_or_404(Problem, code=question)
    return render(request, 'contests/problem.html', {'contest':contest, 'ques':problem})

"""
## This whole region is for checking the user's output agains the given test outputs

"""

def should_update_solved(request, problem):
    already_solved = already(request.user, problem)
    contest_started = problem.contest.start_date <= aware(datetime.datetime.now())
    user_not_admin = problem.contest.admin != request.user

    return not already_solved and contest_started and user_not_admin


def run_code(request, problem, code_info, test_number):
    language = code_info['language']
    import os
    try:
        if language == 'java':

            code_info['outputpath'] = os.path.join(CODEDIR, f'tmp/{request.user.username}/{problem.code}') + ' Main'

            run_cmd = f'timeout {problem.time_lim}s time ' \
                      f'java -cp {code_info["outputpath"]} ' \
                      ' < {} > {}'.format(code_info['inp_file'], code_info['out_file'])
        else:
            run_cmd = f'timeout {problem.time_lim}s time ' \
                       '{} < {} > {}'.format(
                                        code_info['outputpath'],
                                        code_info['inp_file'],
                                        code_info['out_file']
                                       )
        ### Not Secure
        response = sb.check_output(run_cmd.strip(), shell=True, stderr=sb.STDOUT).decode('utf-8')

        retcode = check(request.user, problem.code, test_number)
        if retcode==1:
            current_time_taken = float(response.split()[2].split('e')[0].split(":")[1])
            return current_time_taken

        elif retcode==0:
            return JsonResponse({'status':'WA', 'error':f'WA in testcase {test_number+1}'})
        else:
            return JsonResponse({'status':'SE', 'error':'Results can\'t be matched properly. Contact Admin.'})

    except sb.CalledProcessError as e:
        if 'status 124' in str(e):
            return JsonResponse({'status':'TLE', 'error':f'TLE {problem.time_lim+0.1}'})
        if 'status 1' in str(e):
            return JsonResponse({'status':'RTE', 'error':'Run Time Error'})


def run_python(request, problem, code_info, test_number):
    language = code_info['language']

    language = 'python3.6' if language == 'python3' else 'python2.7'

    run_cmd = 'timeout {}s time {} {} < {} > {}'

    run_cmd = run_cmd.format(
                    problem.time_lim,
                    language,
                    code_info['codepath'],
                    code_info['inp_file'],
                    code_info['out_file']
              )

    try:
        response = sb.check_output(run_cmd.strip(), shell=True, stderr=sb.STDOUT).decode('utf-8')
        retcode = check(request.user, problem.code, test_number)

        if retcode == 1:
            current_time_taken = float(response.split()[2].split('e')[0].split(":")[1])
            return current_time_taken

        elif retcode == 0:
            return JsonResponse({'status':'WA', 'error':f'WA in testcase {test_number+1}'})

        else:
            return JsonResponse({'status':'SE', 'error':f'Results can\'t be matched properly'})

    except sb.CalledProcessError as e:

        if 'status 124' not in str(e):
            output_string = e.output.decode('utf-8').split('\n')[:4]
            output_string = '<pre>{}</pre>'.format('<br>'.join(output_string))
            return JsonResponse({'status':'CE', 'error':output_string})

        if should_add_solved:
            addWA(request, problem)

        return JsonResponse({'status':'TLE', 'error':'Time Limit Exceeded'})

def compile_code(request, problem, code_info):
    language = code_info['language']
    if 'python' in language:
        return
    if language == 'cpp':
        compile_cmd = 'g++ {} -o {}'.format(code_info['codepath'],
                                            code_info['outputpath'])
    elif language == 'c':
        compile_cmd = 'gcc {} -o {}'.format(code_info['codepath'],
                                            code_info['outputpath'])
    else:
        import os
        ddir = os.path.join(CODEDIR, f'tmp/{request.user.username}/{problem.code}/code.java')
        compile_cmd = f'javac {ddir}'

    try:
        ## Not secure
        sb.check_output(compile_cmd.strip(), shell=True, stderr=sb.STDOUT).decode('utf-8')

    except sb.CalledProcessError as e:
        removeDir(request, problem.code)
        if 'status 124' not in str(e):
            retdata = "<pre>{}</pre>".format("<br>".join(e.output.decode('utf-8').split('\n')))
            return JsonResponse({'status':'compile_error', 'error':retdata})
        return JsonResponse({'status':'SE', 'error':'Unknow System Error, contact admin.'})

@csrf_protect
@is_activated
def submit(request, question):
    """
    The view which submits the code and returns verdict as JSON object
    Variables
    # code_data                 : The code sent by user
    # language                  : The programming language used
    # maximum_time_taken        : The maximum time taken till the ith test
    # q                         : the Problem to which code is submitted
    # path_for_problem          : The temporary directory created to save user's output
    # path_for_tests            : Path where problems tests are stored
    # codepath                  : The file where user's code is stored temporarily
    # outputpath                : The file where output of user's output is stored
    # compile_cmd               : The command to be run to compile user's code
    # run_cmd                   : The command to be run to execute user's code
    # inp_file                  : The input test file
    # out_file                  : The expected output test file
    """
    if request.method == 'POST':

        from inout.views import is_alright

        code_data = request.POST.get('code')
        language = request.POST.get('lang')

        if not is_alright(code_data, language):
            return JsonResponse({'status':'Code execution failure', 'error':'Invalid Code.'})

        maximum_time_taken = 0.0

        q = get_object_or_404(Problem, code=question)

        import os

        path_for_problem = os.path.join(CODEDIR, f'tmp/{request.user.username}/{question}')

        if not os.path.exists(path_for_problem):
            os.makedirs(path_for_problem)

        path_for_tests = os.path.join(CODEDIR, f'tmp/problems/{question}')
        codepath = os.path.join(path_for_problem, 'code{}'.format(extensions[language]))
        outputpath = os.path.join(path_for_problem, output[language])
        code_info = {
            'path_for_problem': path_for_problem,
            'path_for_tests': path_for_tests,
            'codepath': codepath,
            'outputpath': outputpath,
            'language': language,
        }
        with open(codepath, 'w') as file:
            file.write(code_data)

        """
        ## This is compiling the code
        """
        compile_verdict = compile_code(request, q, code_info)
        if compile_verdict:
            return compile_verdict
        """
        ## Ending the compilation process If successful, move on to run the code and check output
        """

        for i in range(q.n_testfiles):

            inp_file = os.path.join(path_for_tests, f'in{i}.txt')
            out_file = os.path.join(path_for_problem, f'uout{i}.txt')
            code_info.update({
                'inp_file': inp_file,
                'out_file': out_file,
            })
            ## Separate Code for Python
            if 'python' in language:
                execution_verdict = run_python(request, q, code_info, i)
            else:
                execution_verdict = run_code(request, q, code_info, i)

            if isinstance(execution_verdict, JsonResponse):
                if should_update_solved(request, q):
                    addWA(request, q)
                removeDir(request, question)
                return execution_verdict

            maximum_time_taken = max(maximum_time_taken, execution_verdict)

        removeDir(request, question)

        if should_update_solved(request, q):
            addAC(request, q)

        if not already(request.user, q):
            addSolve(request, q)

        return JsonResponse({'status':'Accepted', 'error':f'Time Taken: {maximum_time_taken}'})

    return  JsonResponse({'status':'NT', 'error':'can\'t find any testcase for this problem'})

def removeDir(request, code):
    """
    utility function to remove temporary directory created
    """
    import os, shutil
    path_to_clear = os.path.join(CODEDIR, f'tmp/{request.user.username}/{code}')
    if(os.path.exists(path_to_clear)):
        shutil.rmtree(path_to_clear)

def check(user, problem, n):
    """
    Utility function to compare user's output and expected output and return the verdict
    """
    try:
        import os
        user_output = open(os.path.join(CODEDIR, f'tmp/{user}/{problem}/uout{n}.txt'), 'r')
        exp_output = open(os.path.join(CODEDIR, f'tmp/problems/{problem}/out{n}.txt'), 'r')
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
    """
    Utility function to check whether user has already solved the particular problem
    or not
    """
    return Solve.objects.filter(Q(problem=q)&Q(user=user)).exists()

def addSolve(request, q):
    """
    Utility funtion to mark that user has solved the particular problem
    """
    Solve.objects.create(user=request.user, problem=q)

def addAC(request, q):
    """
    Utility function which updates rank of user by adding Correct submission
    """
    try:
        p = Ranking.objects.get(user=request.user, contest=q.contest)
        p.ac += 1
        p.score += q.score
    except:
        p = Ranking.objects.create(user=request.user, contest=q.contest)
        p.ac = 1
        p.score = q.score
    p.last_sub = datetime.datetime.now()
    p.save()

def addWA(request, q):
    """
    Utility function which updates rank of user by adding Wrong submission
    """
    try:
        p = Ranking.objects.get(user=request.user, contest=q.contest)
        p.wa += 1
    except:
        p = Ranking.objects.create(user=request.user, contest=q.contest)
        p.wa = 1
    p.save()


"""

## Here is the end of Submission check view and related functions

"""

@is_activated
def deleteq(request, question):
    """
    This view is to delete a question
    Variables
    # q: The problem to be deleted
    """
    q = get_object_or_404(Problem, code=question)

    if q.contest.admin == request.user:
        q.delete()
        import os
        try:
            import shutil
            shutil.rmtree(os.path.join(CODEDIR, f'tmp/problems/{question}'))
        except:
            pass
    else:
        raise Http404
    return HttpResponse("Done")


@is_activated
def rankings(request, contest):
    """
    The view to show the ranking of a particular contest.
    Variables
    # con: The contest whose ranking is to be shown
    # data: THe sorted ranking according to effective scores of users
    """
    con = get_object_or_404(Contest, contest_code=contest)
    if(con.start_date <= aware(datetime.datetime.now())):
        data = sorted(Ranking.objects.filter(Q(contest=con)), key=lambda t:(-t.effective_score, t.penalty))
        return render(request, 'contests/ranking.html', {'con':data, 'contest':con})
    else:
        return render(request, 'contests/ranking.html', {'con':None, 'contest':con})



@is_activated
def deletec(request, contest):
    """
    View to delete a particular contest
    Returns JSON response of success of failure
    Variables
    # con: Contest to be deleted
    """
    con = get_object_or_404(Contest, contest_code=contest)

    if con.start_date >= aware(datetime.datetime.now()):
        request.user.profile.tobecon = False
        request.user.profile.save()
        import os, shutil
        for problem in con.problem_set.all():
            path_to_remove = os.path.join(CODEDIR, f'tmp/problems/{problem.code}')
            if os.path.exists(path_to_remove):
                shutil.rmtree(path_to_remove)
        con.delete()
        return JsonResponse({'done':'Yes, Did that.'}, status=200)
    return JsonResponse({'done':'Nope cant do that'}, status=200)


@is_activated
def get_time(request, contest):
    contest = get_object_or_404(Contest, contest_code=contest)

    return JsonResponse({'start':contest.start_date,
                         'end':contest.end_date}, status=200)

@is_activated
def boardC(request, contest):
    """
    View for main comments on the Contest
    Variables
    # con: Contest on which comments are to be shown
    # comment_list: The comments in the contests
    # comments: paginated comments
    """
    con = get_object_or_404(Contest, contest_code=contest)
    if request.method == 'POST':
        CommentC.objects.create(
            contest=con,
            user=request.user,
            text = request.POST.get('com'),)
    comments_list = CommentC.objects.filter(Q(contest=con)).order_by('-timestamp')
    paginator = Paginator(comments_list, 10)
    page = request.GET.get('page')
    try:
        comments = paginator.page(page)
    except:
        comments = paginator.page(1)

    return render(request, 'contests/discussionC.html', {'comments':comments, 'con':con})


@is_activated
def boardQ(request, question):
    """
    View for main comments on the problem
    Variables
    # prob: Problem on which comments are to be shown
    # comment_list: The comments in the contests
    # comments: paginated comments
    """
    prob = get_object_or_404(Problem, code=question)
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
    """
    View to show responses to a particular comment on a Problem
    Variables
    # main_comment: Comment on which response is to be shown
    # prob: Problem on which these conversations are made
    """
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
def convC(request, contest, pk):
    """
    View to show responses to a particular comment on a Contest
    Variables
    # main_comment: Comment on which response is to be shown
    # con: Contest on which these conversations are made
    """
    main_comment = get_object_or_404(CommentC, id=pk)
    con = get_object_or_404(Contest, contest_code=contest)
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
