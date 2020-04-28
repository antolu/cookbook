from django.contrib import admin

from .models import Recipe, Tag #Question, Choice

# Register your models here.
# admin.site.register(Question)
# admin.site.register(Choice)
admin.site.register(Recipe)
admin.site.register(Tag)
