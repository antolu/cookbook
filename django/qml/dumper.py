# TODO: fill this file
from typing import TextIO, Union

from io import TextIOWrapper

from . import to_string


def dump(data: dict, stream: Union[TextIOWrapper, TextIO]):
    """
    Dumps data from a dict to a file stream. Iterates through the dictionary in order to write the contents.

    Parameters
    ----------
    data : dict
        Ideally should be an OrderedDict
    stream : TextIOWrapper
        The stream to write the data to
    """
    write_kv = lambda k, v: stream.write(f'{k}: {to_string(v)}\n')

    mid_subkey = False  # write newline before new key in environment
    for key, value in data.items():
        if isinstance(value, list):  # environment
            mid_subkey = False
            if len(value) == 0:  # skip empty environments
                continue

            stream.write(f'\n{key}:\n')
            if mid_subkey:
                stream.write('\n')
                mid_subkey = False
            for env_item in value:
                if isinstance(env_item, tuple):  # kv pair
                    stream.write('\n')
                    write_kv(env_item[0], env_item[1])
                else:
                    mid_subkey = True
                    env_item = to_string(env_item)
                    stream.write(str(env_item) + '\n')  # normal items
        else:  # kv pair
            write_kv(key, value)
