from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Problem(models.Model):
	id = models.IntegerField(primary_key=True)