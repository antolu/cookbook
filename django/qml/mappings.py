from datetime import timedelta

from enum import Enum
from datetime import timedelta, date, datetime
import re
from string import Template

from .utilities import DotDict


class Fields(Enum):
    """
    Enumerations to provide an abstraction for the keys used in writing recipes
    """

    # Identification of recipes
    NAME = 'name'
    UUID = 'uuid'
    SLUG = 'slug'

    # Descriptors for recipes
    MAKES = 'makes'
    LANGUAGE = 'language'
    COOKING_TIME = 'cooking_time'
    TEMPERATURE = 'temperature'
    DESCRIPTION = 'description'

    # Core information for recipes
    INGREDIENTS = 'ingredients'
    INSTRUCTIONS = 'instructions'

    # Auxiliary information for recipes
    CHANGELOG = 'changelog'
    TIPS = 'tips'
    NOTES = 'notes'

    # Subkeys for environments in recipes
    PART = 'part'
    ENTRY = 'entry'
    DATE = 'date'
    OPTIONAL = 'optional'


_environments = {
    Fields.INGREDIENTS: {'keys': [Fields.PART, Fields.OPTIONAL], 'uses_dict': True},
    Fields.INSTRUCTIONS: {'keys': [Fields.PART, Fields.OPTIONAL], 'uses_dict': True},
    Fields.CHANGELOG: {'keys': [Fields.ENTRY, Fields.DATE]},
    Fields.NOTES: {},
    Fields.TIPS: {}
}

_keys = {
    Fields.MAKES,
    Fields.TEMPERATURE,
    Fields.COOKING_TIME,
    Fields.NAME,
    Fields.LANGUAGE,
    Fields.DESCRIPTION,
    Fields.UUID
}

_str_mapping = {
    'name': Fields.NAME,
    'recipe': Fields.NAME,
    'uuid': Fields.UUID,
    'slug': Fields.SLUG,
    'language': Fields.LANGUAGE,

    'makes': Fields.MAKES,
    'cookingtime': Fields.COOKING_TIME,
    'cooking time': Fields.COOKING_TIME,
    'description': Fields.DESCRIPTION,
    'temperature': Fields.TEMPERATURE,

    'ingredients': Fields.INGREDIENTS,
    'instructions': Fields.INSTRUCTIONS,
}

_keywords = {
    Fields.OPTIONAL: {
        'yes': True,
        'true': True,
        'no': False,
        'false': False,
    }
}


class Mapping:
    @classmethod
    def is_key(cls, key: str) -> bool:
        if key not in _str_mapping:
            return False

        return _str_mapping[key] in _keys

    @classmethod
    def is_environment(cls, key: str) -> bool:
        if key not in _str_mapping:
            return False

        return _str_mapping[key] in _environments

    @classmethod
    def uses_dict(cls, key: str) -> bool:
        if key not in _str_mapping:
            raise ValueError(f'Passed key [{key}] is not a valid environment')

        env = _environments[_str_mapping[key]]
        return 'uses_dict' in env and env['uses_dict']

    @classmethod
    def is_subkey(cls, key: str) -> bool:
        return key in _str_mapping

    @classmethod
    def is_alias(cls, key: str) -> bool:
        return key in _str_mapping

    @classmethod
    def alias(cls, item):
        if not isinstance(item, str):
            raise ValueError(f'Passed argument [{item}] should be of type str.')
        if item not in _str_mapping:
            raise ValueError(f'Key [{item}] is not a valid alias for a key')

        return _str_mapping[item]


def handle_duration(data: str) -> timedelta:
    regex = re.compile(r'^((?P<hours>\d+)\s?(hour(s)?|h))?\s?((?P<minutes>\d+)\s?(minute(s)?|m))?$', re.IGNORECASE)

    parts = regex.match(data)

    if parts is None:
        raise ValueError(f'Could not parse data {data} as a timedelta')

    parts = parts.groupdict()
    time_params = dict()
    for (name, param) in parts.items():
        try:
            if param:
                time_params[name] = int(param)
        except ValueError:
            pass

    return timedelta(**time_params)


def handle_temperature(data: str) -> int:
    regex = re.compile(r'^(?P<temperature>\d+)\s?(degrees|C)$', re.IGNORECASE)

    m = regex.match(data)
    if not m:
        raise ValueError(f'Could not parse data {data} as temperature')

    m = m.groupdict()
    if m['temperature']:
        return m['temperature']
    else:
        raise ValueError(f'Could not find temperature from string {data}')


def handle_bool(data: str) -> bool:
    data = data.lower()

    if data == 'no' or data == 'false':
        return False
    elif data =='yes' or data == 'true':
        return True
    else:
        raise ValueError('Passed value [{data}] is not a valid boolean.')

def handle_date(data: str) -> date:
    return datetime.strptime(data, '%Y-%m-%d')

class DeltaTemplate(Template):
    delimiter = '%'

class TypeParser:
    regex = DotDict({
        re.compile(r'^(\d+)\s?(degrees|C)$', re.IGNORECASE): {  # temperature
            'function': handle_temperature,
        },
        re.compile(r'^(\d+\s?(hours|h))?\s?(\d+\s?(minutes|m))?$', re.IGNORECASE): {  # duration
            'function': handle_duration,
        },
        re.compile(r'^\d{2}-?\d{1,2}-?\d{1,2}$', re.IGNORECASE): {
            'function': handle_date,
        },
        re.compile(r'^(no|yes|true|false)$', re.IGNORECASE): {
            'function': handle_bool,
        }
    })

    @classmethod
    def parse(cls, item: str):
        for r in cls.regex.keys():
            if r.match(item) is not None:
                return cls.regex[r].function(item)

        return item  # No matches

    @classmethod
    def strfdelta(cls, tdelta: timedelta, fmt: str) -> str:
        d = dict()
        hours, remainder = divmod(tdelta.seconds, 3600)
        d['H'] = hours
        d['M'], d['S'] = divmod(remainder, 60)
        t = DeltaTemplate(fmt)
        return t.substitute(**d)

    @classmethod
    def duration_str(cls, tdelta: timedelta) -> str:
        hours, remainder = divmod(tdelta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        output = ''
        if hours > 0:
            output += '{} hour{}'.format(hours, '' if hours == 1 else 's')
        if minutes > 0:
            output += '{} minute{}'.format(minutes, '' if minutes == 1 else 's')

        return output
