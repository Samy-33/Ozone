from django.db import models
from contests.models import (Problem, Contest)
from django.contrib.auth.models import User
# Create your models here.

class Tag(models.Model):

    creator =  models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    code = models.CharField(max_length=15, unique=True, blank=False, null=False)
    name = models.CharField(max_length=20, blank=False, null=False)

    def __str__(self):
        return f'{self.name} tag created by {self.creator.username}'
#
#
class ProblemTag(models.Model):

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
