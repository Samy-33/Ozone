from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from contests.models import Problem


class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	activation_code = models.CharField(max_length=6, blank=True)
	birth = models.DateField(null=True, blank=True)
	rating = models.IntegerField(default=1200, blank=True, null=True)
	tobecon = models.BooleanField(blank=False, null=False, default=False)
	activated = models.BooleanField(blank=False, null=False, default=False)
	
	@property
	def color(self):

		if self.rating <= 1200:
			return 'grey'
		elif self.rating <= 1400:
			return 'green'
		elif self.rating <= 1700:
			return 'cyan'
		elif self.rating <= 2000:
			return 'blue'
		elif self.rating <= 2500:
			return 'magenta'
		else:
			return 'red'
	
	def __str__(self):
		return self.user.username


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)
		import os
		path = os.path.join(os.getcwd(), "tmp/%s"%instance.username)
		if(not os.path.exists(path)):
			os.mkdir(path)

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
	
