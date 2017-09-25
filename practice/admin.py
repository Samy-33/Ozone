from django.contrib import admin

from .models import ProblemTag, Tag

# Register your models here.
admin.site.register(Tag)
admin.site.register(ProblemTag)
