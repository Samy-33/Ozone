from datetime import datetime as dt
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver


class Contest(models.Model):
	admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	name = models.CharField(max_length=30, blank=False, null=False)
	contest_code = models.CharField(max_length=10, primary_key=True, unique=True, blank=False)
	start_date = models.DateTimeField(null=False, blank=False)
	end_date = models.DateTimeField(null=False, blank=False)
	allowed = models.IntegerField(default=0, blank=False, null=False)
	def __str__(self):
		return f'Admin: {self.admin.username}\nname: {self.name}\ncontest_code: {self.contest_code}\nallowed: {self.allowed}\n'
	
	
class Problem(models.Model):
	setter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
	name = models.CharField(max_length=15, blank=False, null=False)
	code = models.CharField(max_length=10, blank=False, null=False, unique=True)
	text = models.CharField(max_length=10000, blank=False, null=False)
	n_testfiles = models.IntegerField(default=0, blank=False, null=False)
	time_lim = models.FloatField(default=1.0, blank=False, null=False)
	score = models.IntegerField(default = 0)


@receiver(models.signals.pre_delete, sender=Contest)
def delete_data(sender, instance, **kwargs):
	import os, shutil
	for problem in instance.problem_set.all():
		path_to_remove = os.path.join(os.getcwd(), f'tmp/problem/{problem.code}')
		print(path_to_remove)
		if os.path.exists(path_to_remove):
			shutil.rmtree(path_to_remove)
	
	
	
class Solve(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	time = models.DateTimeField(auto_now = True)

class Ranking(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
	wa = models.IntegerField(default=0)
	ac = models.IntegerField(default=0)
	score = models.IntegerField(default=0)
	
	@property
	def effective_score(self):
		return self.score - 5*self.wa

class CommentC(models.Model):
	contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	text = models.CharField(max_length=20, default='')
	timestamp = models.DateTimeField(auto_now=True)
	
class CommentQ(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	text = models.CharField(max_length=20, default='')
	timestamp = models.DateTimeField(auto_now=True)

class ConvC(models.Model):
	comment = models.ForeignKey(CommentC, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	text = models.CharField(max_length=500, default='')
	timestamp = models.DateTimeField(auto_now=True)
	
class ConvQ(models.Model):
	comment = models.ForeignKey(CommentQ, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	text = models.CharField(max_length=500, default='')
	timestamp = models.DateTimeField(auto_now=True)