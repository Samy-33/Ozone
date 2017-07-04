from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from contests.models import Problem


class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	activation_code = models.CharField(max_length=6, blank=True)
	birth = models.DateField(null=True, blank=True)
	rating = models.IntegerField(blank=True, null=True)
	tobecon = models.BooleanField(blank=False, null=False, default=False)
	def __str__(self):
		return self.user.username


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)
		import os
		os.mkdir(os.path.join(os.getcwd(), "tmp/%s"%instance.username))

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
	instance.profile.save()
	
class solved(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	problem = models.OneToOneField(Problem, on_delete=models.CASCADE)
	tm = models.DateTimeField(auto_now_add=True, blank=False)
	time_taken=models.DecimalField(null=False, blank=False, max_digits=5, decimal_places=2)
	#Add memory limit too
#	memory_used=models.DecimalField(null=False, blank=False, max_digits=10, decimal_places=2)
	
