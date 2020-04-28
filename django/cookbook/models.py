from django.db import models
from django.db.models import Model, CharField, DateTimeField, DurationField, FileField, ImageField, SlugField, DateField, ManyToManyField
from django.contrib.postgres.fields import JSONField, ArrayField
from django.db.models import ForeignKey, IntegerField
from django.utils import timezone
from django_extensions.db.fields import AutoSlugField
from django.utils.translation import gettext_lazy as _

# Create your models here.

# class Question(Model):
#     question_text = CharField(max_length=200)
#     pub_date = DateTimeField('date_published')

#     def __str__(self):
#         return self.question_text

# class Choice(Model):
#     question = ForeignKey(Question, on_delete=models.CASCADE)
#     choice_text = models.CharField(max_length=200)
#     votes = models.IntegerField(default=0)


class Tag(Model):
    word = CharField(max_length=100)

    slug = AutoSlugField(_('slug'), editable=True, unique=True, populate_from='word', help_text='A tag.')

    def __str__(self):
        return self.word


class Recipe(Model):
    title = CharField(max_length=100, help_text='The name of the recipe.')
    slug = AutoSlugField(_('slug'), editable=True, unique=True, populate_from='title', help_text='An easy-to-remember short name.')

    yields = CharField(max_length=100, help_text='How much the recipe yields, for 4 people, 8 pieces, etc.')

    external_recipes = ManyToManyField('Recipe')

    cooking_time = DurationField(blank=True)
    
    data = JSONField()
    changelog = JSONField()

    pub_date = DateTimeField('date_published', default=timezone.now)
    last_changed = DateField(default=timezone.now)

    tags = ManyToManyField(Tag)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
        verbose_name_plural = 'recipes'


