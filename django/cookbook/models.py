import uuid

from django.db.models import Model, CharField, DurationField, DateField, ManyToManyField, BooleanField, UUIDField
from django.contrib.postgres.fields import JSONField, ArrayField
from django.utils import timezone
from django_extensions.db.fields import AutoSlugField
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Tag(Model):
    word = CharField(max_length=100)

    slug = AutoSlugField(_('slug'), editable=True, unique=True, populate_from='word', help_text='A tag.')

    def __str__(self):
        return self.word


class Recipe(Model):
    title = CharField(max_length=100, help_text='The name of the recipe.')
    slug = AutoSlugField(_('slug'), editable=True, unique=True, populate_from='title', help_text='An easy-to-remember short name.')
    uuid = UUIDField(editable=False, default=uuid.uuid4, primary_key=True)

    yields = CharField(max_length=100, help_text='How much the recipe yields, for 4 people, 8 pieces, etc.', blank=True)

    external_recipes = ManyToManyField('Recipe', blank=True)
    #
    cooking_time = DurationField(blank=True, null=True)

    has_parts = BooleanField(default=True, blank=True)
    ingredients = JSONField()
    instructions = JSONField()

    changelog = JSONField(blank=True)
    notes = ArrayField(CharField(max_length=255), blank=True)

    pub_date = DateField('date_published', default=timezone.now, editable=False)
    last_changed = DateField(default=timezone.now)

    tags = ManyToManyField(Tag, blank=True)

    # image = ImageField(upload_to='images/')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
        verbose_name_plural = 'recipes'


