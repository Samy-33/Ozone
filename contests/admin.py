from django.contrib import admin

from .models import Contest, Problem

# Register your models here.
admin.site.register(Problem)
admin.site.register(Contest)
