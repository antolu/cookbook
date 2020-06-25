import re

from .typeparser import parse_type
from .utilities import DotDict, Iterator
from .exceptions import IsComment

import logging
from pprint import pformat

log = logging.getLogger(__name__)


class _AbstractLoader:
    def __init__(self, stream, config: DotDict):
        self.stream = stream
        self.config = config
        self.loaded = False

        self.index = 0


class Loader(_AbstractLoader):
    """
    Loader to load data
    """
    def __init__(self, stream, config: DotDict):
        super().__init__(stream, config)

    def load(self) -> DotDict:
        if self.loaded:
            raise RuntimeError('This stream has already been loaded.')

        input_data = self.stream.read()

        # Remove excess newlines
        input_data = re.sub(r'\n\s*\n', '\n', input_data)

        data = DotDict()

        iterator = Iterator([line.strip() for line in input_data.splitlines()])

        while iterator.has_next():
            try:
                key, value = self.__parse(iterator, data)
                data[key] = value
            except IsComment:
                pass

        self.loaded = True

        return data

    def __parse(self, iterator: Iterator, data: dict):
        line = iterator.next()
        self.index += 1
        if line.startswith('#'):  # comment
            raise IsComment()

        if ':' not in line:
            raise ValueError(f'Line {self.index}: [{line}] is not a valid key: value pair')

        if not line.endswith(':'):  # contains key: val
            key, val = [s.strip() for s in line.split(':', 1)]
        else:
            env_name = line[0:len(line) - 1]  # remove the trailing :
            if self.config.is_environment(env_name):
                return env_name, self.__parse_environment(iterator, env_name, data)
            else:
                raise ValueError(f'Line {self.index}: passed key [{env_name}] is not a valid environment.')

        key = key.lower()
        if self.config.is_alias(key):
            key = self.config.aliases[key]
        elif self.config.is_key(key):
            pass
        else:
            raise ValueError(f'Line {self.index}: passed key [{key}] is not a valid key')

        val = parse_type(val)

        log.info(f'Parsed key {key} with value {val}.')
        return key, val

    def __parse_environment(self, iterator: Iterator, env_name: str, data: dict):
        output = list()

        while iterator.has_next():

            peek_key = iterator.peek().split(':')[0]
            if self.config.is_key(peek_key) or self.config.is_environment(peek_key):  # Other key
                return output

            line = iterator.next()
            self.index += 1
            if line.startswith('#'):  # skip comments
                continue

            line = [s.strip() for s in line.split(':', 1)]
            if len(line) == 2:  # Has keys
                key, val = line
                try:
                    if self.config.is_subkey(env_name, key):
                        val = parse_type(val)
                except ValueError as err:
                    raise ValueError(f'Line {self.index}: ' + str(err))
                output.append((key, val))
            else:
                output.append(line[0])

        return output
