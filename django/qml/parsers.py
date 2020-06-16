import json
import logging
from collections import OrderedDict

import re
from pprint import pformat
from datetime import date, timedelta, datetime
from uuid import uuid4

from django.core.serializers.json import DjangoJSONEncoder
from django.utils.text import slugify
from .mappings import Fields

from .utilities import Iterator, DotDict
from .parser import load

log = logging.getLogger(__name__)


def parse_file(f):
    # data = load(f, Loader=FullLoader)
    data = load(f)

    parsed_recipe = parse_recipes(data)

    return parsed_recipe


def parse_recipes(data):
    output = dict()

    field_mapping = {
        'name': Fields.NAME,
        'uuid': Fields.UUID,
        'yields': Fields.MAKES,
        'description': Fields.DESCRIPTION,
        'temperature': Fields.TEMPERATURE,
        'cooking_time': Fields.COOKING_TIME,
        'notes': Fields.NOTES,
        'tips': Fields.TIPS,
    }

    # check if recipe is divided into steps
    language = data[Fields.LANGUAGE]
    output['language'] = language

    for o, d in field_mapping.items():
        if d in data:
            output[o] = data[d]

    if Fields.PART in data:
        output['has_parts'] = True
        output['ingredients'] = list()
        output['instructions'] = list()

        for part in data['parts']:
            ingredients = list()
            steps = list()
            notes = list()

            for ingredient in part['ingredients']:
                ingredients.append(ingredient)
            for step in part['instructions']:
                steps.append(step)

            is_optional = False
            if 'optional' in part and part['optional']:
                is_optional = True

            output['ingredients'].append(
                {'list': ingredients, 'optional': is_optional,
                 'name': part['name'] if 'name' in part else None})
            output['instructions'].append(
                {'list': steps, 'optional': is_optional, 'name': part['name'] if 'name' in part else None})

    else:  # only no parts in recipe
        output['has_parts'] = False
        output['ingredients'] = list()
        output['instructions'] = list()

        for ingredient in data['ingredients']:
            output['ingredients'].append(ingredient)
        for step in data['instructions']:
            output['instructions'].append(step)

        if 'notes' in data:  # notes exist
            output['notes'] = list()
            output['has_notes'] = True
            for note in data:
                output['notes'].append(note)
        else:
            output['has_notes'] = False

    if Fields.CHANGELOG in data:  # changelog exists
        output['has_changelog'] = True

        output['changelog'] = list()
        for entry in data[Fields.CHANGELOG]:
            if type(entry['date']) is str:
                entry['date'] = datetime.strptime(entry['date'], '%Y-%m-%d').date()
            if type(entry['change']) is not list:
                entry['change'] = [entry['change']]
            output['changelog'].append(entry)

    else:
        output['has_changelog'] = False

    return output


def dict_to_json(data: dict):
    """
    Convert a YAML/dictionary form data to JSON compatible for insertion to Django DB
    """

    output = dict()

    # Map output keys to input keys and default value
    copyable_fields = {
        'last_changed': ('last_changed', date.today()),
        'pub_date': ('date_published', date.today()),
        'title': ('name', ''),
        'description': ('description', ''),
        'uuid': ('uuid', uuid4()),
        'yields': ('yields', ''),
        'has_parts': ('has_parts', False),
        'notes': ('notes', list()),
        'temperature': ('temperature', 0),
        'cooking_time': ('cooking_time', timedelta()),
        'language': ('language', 'en'),
        'tips': ('tips', list()),
        # 'tags': ('tags', list()),
    }

    if data['has_changelog'] or 'changelog' in data:
        output['changelog'] = json.dumps(data['changelog'], cls=DjangoJSONEncoder, separators=(', ', ': '))

        # find last changed date:
        earliest = date.today()
        latest = date(2000, 1, 1)
        found_date = False
        for change in data['changelog']:
            if 'date' in change:
                found_date = True
                if change['date'] < earliest:
                    earliest = change['date']
                if change['date'] > latest:
                    latest = change['date']

        if found_date:
            log.info('Parsed dates from changelog: {}/{}'.format(earliest, latest))
            output['pub_date'] = earliest
            output['last_changed'] = latest
        else:
            log.info('No dates found, using today as default.')
            output['pub_date'] = date.today()
            output['last_changed'] = date.today()
    else:
        output['changelog'] = json.dumps(
            [
                {
                    'change': [
                        'First publication',
                    ],
                    'date': date.today()
                }
            ],
            cls=DjangoJSONEncoder,
            separators=(',', ':'),
        )

    if data['has_parts'] or len(data['ingredients']) == len(data['instructions']):
        log.info('Recipe has parts, jsonifying.')
        output['instructions'] = json.dumps(data['instructions'], cls=DjangoJSONEncoder, separators=(', ', ': '))
        output['ingredients'] = json.dumps(data['ingredients'], cls=DjangoJSONEncoder, separators=(', ', ': '))
    else:
        log.info('Recipe is in one chunk. Still jsonifying.')
        output['instructions'] = json.dumps(data['instructions'], cls=DjangoJSONEncoder, separators=(', ', ': '))
        output['ingredients'] = json.dumps(data['ingredients'], cls=DjangoJSONEncoder, separators=(', ', ': '))

    for o, d in copyable_fields.items():
        if d[0] in data:
            log.info('Field {} exists in data, overriding with {}.'.format(d[0], data[d[0]]))
            output[o] = data[d[0]]
        else:
            log.info('Field {} does not exist in data. Skipping.'.format(d[0]))
            if o not in output:  # Only enter empty information if it does not already exist
                output[o] = d[1]

    output['slug'] = slugify(data['name'])

    return output


def recipe_to_dict(recipe):
    output = OrderedDict()

    output['name'] = recipe.title
    output['slug'] = recipe.slug
    output['uuid'] = str(recipe.uuid)
    output['language'] = recipe.language
    output['yields'] = recipe.yields
    if recipe.description is not None:
        output['description'] = recipe.description
    if recipe.temperature != 0:
        output['temperature'] = recipe.temperature

    output['date_published'] = recipe.pub_date
    if recipe.cooking_time != timedelta():
        output['cooking_time'] = recipe.cooking_time
    output['has_parts'] = recipe.has_parts
    output['ingredients'] = json.loads(recipe.ingredients)
    output['steps'] = json.loads(recipe.instructions)
    output['changelog'] = json.loads(recipe.changelog)
    output['notes'] = recipe.notes
    output['tips'] = recipe.tips

    return output


def format_for_output(data: OrderedDict):
    if data['has_parts']:
        data['parts'] = list()
        for i in range(len(data['ingredients'])):
            ingredientpart = data['ingredients'][i]
            steppart = data['steps'][i]

            name = ingredientpart['name']
            optional = ingredientpart['optional']
            items = ingredientpart['list']
            steps = steppart['list']

            data['parts'].append(OrderedDict([
                ('name', name),
                ('ingredients', items),
                ('steps', steps),
            ]))
            if not optional:
                data['parts'][i]['optional'] = optional

        del data['ingredients']
        del data['steps']
    else:
        pass
        # data['ingredients'] = data['ingredients']['list']
        # data['steps'] = data['steps']['list']

    del data['has_parts']

    data.move_to_end('tips')
    data.move_to_end('notes')
    data.move_to_end('changelog')

    return data
