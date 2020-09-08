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
    """
    Represents a recipe in memory, and contains an internal dictionary that represents the recipe, and allows
    for it to be converted into django database form, or to a qml parsable form. The intenral dictionary is created
    from either a formatted dictionary, from a parsed qml file, or directly from a django Recipe model object.

    See Also
    --------
    django.cookbook.models.Recipe:
        The Django recipe class
    """

    # These fields represent the fields that must exist in either representation.
    required_fields = [
        'name',
        'makes',
        'ingredients',
        'instructions',
    ]

    # These fields represents the fields that may optionally be present in a recipe.
    optional_fields = [
        'language',
        'uuid',
        'slug',
        'description',
        'temperature',
        'cooking_time',
        'notes',
        'tips',
        'changelog',
        'pub_date',
    ]

    # These fields represent environments are not simply kv-pairs, and require special attention.
    environments = [
        'ingredients',
        'instructions',
        'changelog',
    ]

    def __init__(self, data: Union[Recipe, dict], format: str):
        """
        Parameters
        ----------
        data : Recipe or dict
            The data to wrap, or convert to a proper format.
        format : str
            Which format the passed data is, or rather from which format to convert to internal represenation.
        """
        if format == 'io':
            internal = self.__io_to_internal(data)
        elif format == 'internal':
            internal = data
        elif format == 'django':
            if isinstance(data, Recipe):
                data = data.__dict__
            internal = self.__djangodb_to_internal(data)
        else:
            raise ValueError(f'The format {format} is not a valid format.')
        self.internal = internal

    def get_dict(self) -> dict:
        """
        Returns the internal (pythonic) representation of the recipe without any conversion.

        Returns
        -------
        dict:
            A dictionary that represents the wrapped recipe.
        """
        return self.internal

    def to_djangodb(self) -> dict:
        """
        Takes the internal dictionary and converts it into a django db representation.

        Returns
        -------
        dict:
            A dictionary that allows for a django.cookbook.models.Recipe object to be created using the kv-pairs.
        """
        return self.__internal_to_djangodb(self.internal)

    def to_qml(self) -> dict:
        """
        Takes the internal dictionary and converts it into a qml exportable representation.

        Returns
        -------
        dict:

        """
        return self.__internal_to_qml(self.internal)

    def __io_to_internal(self, data: dict) -> dict:
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
                middlehand = [DotDict()]
                for item in data[env]:
                    if isinstance(item, tuple):  # is a key-value pair
                        key, val = item
                        if key == 'part':
                            d = DotDict({'part': val.title(), 'list': list()})
                            if middlehand and (
                                    not middlehand[0] or not middlehand[0]['list']):  # First entry in the list is empty
                                middlehand[0] = d
                            else:
                                middlehand.append(d)
                        elif key == 'optional':
                            middlehand[-1]['optional'] = val
                        elif key == 'date':
                            if 'date' in middlehand[-1] and middlehand[-1]['date'] != val:
                                middlehand.append({'date': val, 'list': list()})
                            else:
                                middlehand[-1]['date'] = val
                        else:
                            raise KeyError('Key {} is not a valid '.format(key))
                    elif isinstance(item, str):
                        if 'list' not in middlehand[-1]:
                            middlehand[-1]['list'] = list()
                        middlehand[-1]['list'].append(item)
                    else:
                        error_messages += f'Item {str(item)} is of invalid format.\n'
                output[env] = middlehand

        if len(error_messages) != 0:
            raise ValueError('Encountered error during parsing:\n' + '\n'.join(error_messages))

        return output

    def __internal_to_qml(self, data: dict) -> dict:
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
                    log.info(pformat(data[env]))
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

    def __internal_to_djangodb(self, data: dict) -> dict:
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

    def __djangodb_to_internal(self, data: dict) -> dict:

        output = OrderedDict()

        for key in self.required_fields:
            output[key] = data[key]

        for key in self.optional_fields:
            if data[key] is not None:
                output[key] = data[key]

        for env in self.environments:
            output[env] = json.loads(data[env])

        return output
