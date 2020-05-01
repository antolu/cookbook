import json
import logging
import sys
from collections import OrderedDict
from datetime import date, timedelta

from django.core.serializers.json import DjangoJSONEncoder
from django.utils.text import slugify
from yaml import load, FullLoader

from .models import Recipe

log = logging.getLogger(__name__)


def parse_file(f, options):
    data = load(f, Loader=FullLoader)

    parsed_recipe = parse_recipes(data, options)

    return parsed_recipe


def parse_recipes(data, options):
    if 'recipe' not in data:
        log.error('Could not find key \'recipe\' in the file.')
        sys.exit(1)

    recipe_data = data['recipe']
    orig_data = data

    recipes = dict()

    # parse languages
    if options['language'] != 'all':
        for item in recipe_data:
            if item['language'] == options['language']:
                break

            # finally
            log.error('Recipe written in {} not found'.format(options['language']))
            sys.exit(1)

        recipes[options['language']] = dict()
    else:
        for item in recipe_data:
            recipes[item['language']] = dict()

    # check if recipe is divided into steps
    for item in recipe_data:
        language = item['language']
        if language not in recipes:
            continue
        data = recipes[language]
        data['language'] = language

        if 'yields' in item:
            data['yields'] = item['yields']
        if 'name' not in item:
            log.warning('Recipe has no name.')
        else:
            data['name'] = item['name']
        if 'parts' in item:
            data['has_parts'] = True
            data['ingredients'] = list()
            data['steps'] = list()
            data['notes'] = list()

            for part in item['parts']:
                ingredients = list()
                steps = list()
                notes = list()

                for ingredient in part['ingredients']:
                    ingredients.append(ingredient)
                for step in part['steps']:
                    steps.append(step)

                is_optional = False
                if 'optional' in part and part['optional']:
                    is_optional = True

                data['ingredients'].append(
                    {'list': ingredients, 'optional': is_optional,
                     'name': part['name'] if 'name' in part else None})
                data['steps'].append(
                    {'list': steps, 'optional': is_optional, 'name': part['name'] if 'name' in part else None})

            if 'notes' in item:  # notes exist for this language
                data['has_notes'] = True
                for note in item['notes']:
                    data['notes'].append(note)

            else:
                data['has_notes'] = False
                log.debug('{} notes parsed for language {}'.format(
                    len(data['notes']), language))

        else:  # only no parts in recipe
            data['has_parts'] = False
            data['ingredients'] = list()
            data['steps'] = list()

            for ingredient in item['ingredients']:
                data['ingredients'].append(ingredient)
            for step in item['steps']:
                data['steps'].append(step)

            if 'notes' in item:  # notes exist
                data['notes'] = list()
                data['has_notes'] = True
                for note in item:
                    data['notes'].append(note)
            else:
                data['has_notes'] = False

        if 'changelog' in orig_data:  # changelog exists
            data['has_changelog'] = True

            data['changelog'] = list()
            for entry in orig_data['changelog']:
                if type(entry['change']) is not list:
                    entry['change'] = [entry['change']]
                data['changelog'].append(entry)

        else:
            data['has_changelog'] = False

    return recipes


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
        'yields': ('yields', ''),
        'has_parts': ('has_parts', False),
        'notes': ('notes', []),
        'cooking_time': ('cooking_time', timedelta()),
        'language': ('language', 'en'),
    }

    for language, language_d in data.items():
        if language != 'en':  # Ignore non-english recipes for now
            continue

        if language_d['has_changelog'] or 'changelog' in language_d:
            output['changelog'] = json.dumps(language_d['changelog'], indent=2, cls=DjangoJSONEncoder)

            # find last changed date:
            earliest = date.today()
            latest = date(2000, 1, 1)
            found_date = False
            for change in language_d['changelog']:
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
                indent=2,
                cls=DjangoJSONEncoder,
            )

        if language_d['has_parts'] or len(language_d['ingredients']) == len(language_d['steps']):
            log.info('Recipe has parts, jsonifying.')
            output['instructions'] = json.dumps(language_d['steps'], indent=2, cls=DjangoJSONEncoder)
            output['ingredients'] = json.dumps(language_d['ingredients'], indent=2, cls=DjangoJSONEncoder)
        else:
            log.info('Recipe is in one chunk. Still jsonifying.')
            output['instructions'] = json.dumps(language_d['steps'], indent=2, cls=DjangoJSONEncoder)
            output['ingredients'] = json.dumps(language_d['ingredients'], indent=2, cls=DjangoJSONEncoder)

        for o, d in copyable_fields.items():
            if d[0] in language_d:
                log.info('Field {} exists in data, overriding with {}.'.format(d[0], language_d[d[0]]))
                output[o] = language_d[d[0]]
            else:
                log.info('Field {} does not exist in data. Skipping.'.format(d[0]))
                if o not in output:  # Only enter empty information if it does not already exist
                    output[o] = d[1]

        # if 'notes' not in language_d:
        #     output['notes'] = []

        output['slug'] = slugify(language_d['name'])

    return output


def recipe_to_dict(recipe: Recipe):
    output = OrderedDict()

    output['language'] = recipe.language
    output['name'] = recipe.title
    output['slug'] = recipe.slug
    output['uuid'] = str(recipe.uuid)
    output['yields'] = recipe.yields
    if recipe.temperature != 'null' or recipe.temperature != 0:
        output['temperature'] = recipe.temperature

    output['date_published'] = recipe.pub_date
    if recipe.cooking_time != timedelta():
        output['cooking_time'] = recipe.cooking_time
    output['has_parts'] = recipe.has_parts
    output['ingredients'] = json.loads(recipe.ingredients)
    output['steps'] = json.loads(recipe.instructions)
    output['changelog'] = json.loads(recipe.changelog)

    return output


def format_for_output(data: dict):
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
                ('optional', optional),
                ('ingredients', items),
                ('steps', steps),
            ]))

        del data['ingredients']
        del data['steps']
    else:
        data['ingredients'] = data['ingredients']['list']
        data['steps'] = data['steps']['list']

    del data['has_parts']

    return data
