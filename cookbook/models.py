import uuid

from django.db.models import Model, CharField, DurationField, DateField, ManyToManyField, BooleanField, UUIDField, \
    IntegerField, TextField, JSONField
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone
from django_extensions.db.fields import AutoSlugField
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Recipe(Model):
    name = CharField(max_length=100, help_text='The name of the recipe.')
    slug = AutoSlugField(_('slug'), editable=True, unique=True, populate_from='name',
                         help_text='An easy-to-remember short name.')
    uuid = UUIDField(editable=False, default=uuid.uuid4, primary_key=True)
    language = CharField(max_length=20, choices=[('en', 'english'), ('sv', "swedish")], default='english')

    makes = CharField(max_length=100, help_text='How much the recipe yields, for 4 people, 8 pieces, etc.')

    description = TextField(blank=True, null=True)

    external_recipes = ManyToManyField('Recipe', blank=True)
   
    cooking_time = DurationField(blank=True, null=True)
    temperature = IntegerField(blank=True, default=0)

    ingredients = JSONField()
    instructions = JSONField()

    changelog = JSONField(blank=True)
    notes = ArrayField(TextField(), null=True)
    tips = ArrayField(TextField(), null=True)

    pub_date = DateField('date_published', default=timezone.now, editable=False)
    last_changed = DateField(default=timezone.now)

    # image = ImageField(upload_to='images/')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'recipes'
