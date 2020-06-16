from .mappings import TypeParser, Mapping
from .utilities import Iterator, DotDict
import logging
import yaml
from typing import Tuple, Union

log = logging.getLogger(__name__)


def load_config(file):
    input_data = yaml.safe_load(file)
    data = DotDict()

    sections = ['keys', 'environments', 'aliases']

    for s in sections:
        if s not in input_data:
            log.warn(f'There are no {s} in the parser configuration file.')
            data[s] = set()
        else:
            data[s] = set(input_data[s])

    data.is_environment = lambda query: query in data.environments
    data.is_key = lambda query: query in data.keys
    data.is_alias = lambda query: query in data.aliases

    return data


def load(file):
    input_data = file.read()
    log.info(input_data)
    input_data = input_data.replace('\n\n', '\n')

    data = DotDict()

    iterator = Iterator(input_data.splitlines())

    while iterator.has_next():
        try:
            key, value = _parse(iterator, data)
            data[key] = value
        except IsComment:
            pass

    return data


def _parse(iterator: Iterator, data: dict):
    line = iterator.next()
    if line.startswith('#'):  # comment
        raise IsComment()

    if ':' not in line:
        raise ValueError(f'Line [{line}] is not a valid key: value pair')

    if not line.endswith(':'):  # contains key: val
        print(line)
        key, val = [s.strip() for s in line.split(':', 1)]
    else:
        env_name = line[0:len(line) - 1]  # remove the trailing :
        if Mapping.is_environment(env_name):
            return env_name, __parse_environment(iterator, env_name, data)
        else:
            raise ValueError(f'Passed key [{env_name}] is not a valid environment.')

    key = key.lower()
    if Mapping.is_alias(key):
        key = Mapping.alias(key)
    elif Mapping.is_key(key):
        pass
    else:
        raise ValueError(f'Passed key [{key}] is not a valid key')

    val = TypeParser.parse(val)

    log.info(f'Parsed key {key} with value {val}.')
    return key, val


def __parse_environment(iterator: Iterator, env_name: str, data: dict):
    uses_dict = Mapping.uses_dict(env_name)
    output = list()
    if uses_dict:
        output.append(DotDict({'list': list()}))

    while iterator.has_next():

        peek_key = iterator.peek().split(':')[0]
        if Mapping.is_key(peek_key) or Mapping.is_environment(peek_key):  # Other key
            return output

        line = iterator.next()
        if line.startswith('#'):  # skip comments
            continue

        line = [s.strip() for s in line.split(':', 1)]
        if len(line) == 2:  # Has keys
            key, val = line
            if Mapping.is_subkey(key):
                val = TypeParser.parse(val)

                if key == 'part':
                    data['has_parts'] = True
                    d = DotDict({'name': val, 'list': list()})
                    if output and (not output[0] or not output[0]['list']):  # First entry in the list is empty
                        output[0] = d
                    else:
                        output.append(d)
                elif key == 'optional':
                    output[-1]['optional'] = val
                elif key == 'entry':
                    if output[-1]['entry'] != val:
                        output.append({'entry': val})
                    else:
                        output[-1]['entry'] = val
                elif key == 'date':
                    try:
                        if output[-1]['date'] != val:
                            output.append({'date': val})
                        else:
                            output[-1]['date'] = val
                    except ValueError:
                        raise ValueError('Value {} is not a valid date format'.format(val))

                else:
                    raise KeyError('Key {} is not a valid ')
        else:
            if uses_dict:
                output[-1].list.append(line[0])
            else:
                output.append(line[0])

    return output


class IsComment(Exception):
    """Raised when the line is a comment"""
    pass
