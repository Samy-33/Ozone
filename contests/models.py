from __future__ import unicode_literals
from datetime import datetime as dt
from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Contest(models.Model):
	admin = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
	name = models.CharField(max_length=30, blank=False, null=False)
	contest_code = models.CharField(max_length=10, unique=True, blank=False)
	start_date = models.DateTimeField(null=False, blank=False)
	end_date = models.DateTimeField(null=False, blank=False)
	allowed = models.IntegerField(default=0, blank=False, null=False)
	def __str__(self):
		return "Admin: %s\nname: %s\ncontest_code: %s\nallowed: %s\n"%(self.admin.username, self.name, self.contest_code, str(self.allowed))
	
	
class Problem(models.Model):
	setter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
	name = models.CharField(max_length=15, blank=False, null=False)
	code = models.CharField(max_length=10, blank=False, null=False, unique=True)
	text = models.CharField(max_length=10000, blank=False, null=False)
	n_testfiles = models.IntegerField(default=0, blank=False, null=False)
	time_lim = models.FloatField(default=1.0, blank=False, null=False)
	score = models.IntegerField(default = 0)

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


	