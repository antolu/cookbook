import json
from collections import OrderedDict
from datetime import date, timedelta
from typing import Union

from django.core.serializers.json import DjangoJSONEncoder
from django.utils.text import slugify

from pprint import pformat

from cookbook.models import Recipe
from qml import DotDict
import logging

log = logging.getLogger(__name__)


class RecipeFile:
    required_fields = {
        'name',
        'makes',
        'ingredients',
        'instructions',
    }

    optional_fields = {
        'language',
        'uuid',
        'description',
        'temperature',
        'cooking_time',
        'notes',
        'tips',
        'changelog',
        'pub_date',
    }

    environments = [
        'ingredients',
        'instructions',
        'changelog',
    ]

    def __init__(self, data: Union[Recipe, dict], format: str):
        if format == 'io':
            internal = self.__io_to_dict(data)
        elif format == 'internal':
            internal = data
        elif format == 'django':
            if isinstance(data, Recipe):
                data = data.__dict__
            internal = self.__django_to_dict(data)
        else:
            raise ValueError(f'The format {format} is not a valid format.')
        self.internal = internal

    def format_dict(self) -> dict:
        return self.internal

    def format_django(self) -> dict:
        return self.__dict_to_django(self.internal)

    def format_io(self) -> dict:
        return self.__dict_to_io(self.internal)

    def __io_to_dict(self, data: dict) -> dict:
        """
        Converts an input from QML loader into a python dictionary with full recipe structure
        """
        output = DotDict()
        error_messages = []
        error_message_template = 'The recipe does not contain a required key [{}]'

        warning_messages = []
        warning_message_template = 'The recipe does not contain an optional key [{}], this will be skipped.'

        for key in self.required_fields:
            if key in data:
                if key not in self.environments:
                    output[key] = data[key]
            else:
                error_messages.append(error_message_template.format(key))

        for key in self.optional_fields:
            if key in data:
                if key not in self.environments:
                    output[key] = data[key]
            else:
                warning_messages.append(warning_message_template.format(key))

        for env in self.environments:
            if env not in data and env in self.required_fields:
                error_messages.append(error_message_template.format(env))
            elif env not in data and env in self.optional_fields:
                log.warning(f'Environment [{env}] is missing. Skipping it.')
            else:
                middlehand = [{'list': list()}]
                for item in data[env]:
                    if isinstance(item, tuple):  # is a key-value pair
                        key, val = item
                        if key == 'part':
                            d = DotDict({'name': val, 'list': list()})
                            if middlehand and (
                                    not middlehand[0] or not middlehand[0]['list']):  # First entry in the list is empty
                                middlehand[0] = d
                            else:
                                middlehand.append(d)
                        elif key == 'optional':
                            middlehand[-1]['optional'] = val
                        elif key == 'entry':
                            if 'entry' in middlehand[-1] and middlehand[-1]['entry'] != val:
                                middlehand.append({'entry': val})
                            else:
                                middlehand[-1]['entry'] = val
                        elif key == 'date':
                            if 'date' in middlehand[-1] and middlehand[-1]['date'] != val:
                                middlehand.append({'date': val})
                            else:
                                middlehand[-1]['date'] = val
                        else:
                            raise KeyError('Key {} is not a valid ')
                    elif isinstance(item, str):
                        middlehand[-1]['list'].append(item)
                    else:
                        error_messages += f'Item {str(item)} is of invalid format.\n'
                output[env] = middlehand

        if len(error_messages) != 0:
            raise ValueError('Encountered error during parsing:\n' + '\n'.join(error_messages))

        return output

    def __dict_to_io(self, data: dict) -> dict:
        # TODO: also need to convert python representations like durations to strings

        output = DotDict()

        for key in self.required_fields:
            if key not in self.environments:
                output[key] = data[key]

        for key in self.optional_fields:
            if key in data and key not in self.environments:
                if key == 'temperature':
                    output[key] = str(data[key]) + ' degrees'
                    continue

                output[key] = data[key]

        for env in self.environments:
            middlehand = list()
            if env in data:
                for sub_env in data[env]:
                    for key, value in sub_env.items():
                        if isinstance(value, list):
                            for val in value:
                                middlehand.append(val)
                        else:
                            if key == 'optional' and not value:  # skip optional if it is false
                                continue

                            middlehand.append((key, value))
            output[env] = middlehand

        return output

    def __dict_to_django(self, data: dict) -> dict:
        """
            Convert a YAML/dictionary form data to JSON compatible for insertion to Django DB
            """

        output = dict()

        json_separators = (', ', ': ')
        for env in self.environments:
            if env in data:
                output[env] = json.dumps(data[env], cls=DjangoJSONEncoder, separators=json_separators)

        if 'changelog' in data:
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
                log.debug(f'Parsed dates from changelog: {earliest}/{latest}')
                output['pub_date'] = earliest
                output['last_changed'] = latest
            else:
                log.debug('No dates found, using today as default.')
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
                separators=json_separators,
            )

        for key in self.required_fields:
            if key not in data:
                raise ValueError(f'Required key [{key}] is not found in the data.')
            if key not in self.environments:
                output[key] = data[key]

        for key in self.optional_fields:
            if key not in data:
                log.warning(f'Optional key [{key}] not found in data. Skipping entry.')
                # TODO: also add warning messages
                continue
            if key not in self.environments:
                output[key] = data[key]

        output['slug'] = slugify(data['name'])

        return output

    def __django_to_dict(self, data: dict) -> dict:

        output = OrderedDict()

        for key in self.required_fields:
            output[key] = data[key]

        for key in self.optional_fields:
            if data[key] is not None:
                output[key] = data[key]

        for env in self.environments:
            output[env] = json.loads(data[env])

        return output
