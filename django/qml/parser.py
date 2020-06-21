from pprint import pformat

from .loader import Loader
from .utilities import DotDict
import logging
import yaml

log = logging.getLogger(__name__)


def load_config(file) -> DotDict:
    """
    Loads a config file to be used as configuration for a qml parser. Currently parses top-level keys
    'keys', 'environments', 'aliases'.

    Parameters
    ----------
    file : TextIOWrapper
        A file stream to read data from

    Returns
    -------
    data: DotDict
        A dictionary containing the configuration information.

    """
    input_data = yaml.safe_load(file)
    data = DotDict()

    sections = ['keys', 'environments', 'aliases']

    for s in sections:
        if s not in input_data:
            log.warn(f'There are no {s} in the parser configuration file.')
            data[s] = set()
        else:
            if s == 'aliases':
                aliases = dict()
                for line in input_data[s]:
                    splits = line.split('=')
                    if len(splits) == 1:
                        raise ValueError(f'Line [{line}] does not contain a = assignment')
                    elif len(splits) > 2:
                        raise ValueError(f'Line [{line}] contains too many = assignments')
                    aliases[splits[0]] = splits[1]
                data[s] = aliases
            elif s == 'environments':
                middlehand = dict()
                for item in input_data[s]:
                    if isinstance(item, dict):
                        if 'key' not in item:
                            raise ValueError('Key [key] does not exist.')
                        if 'subkeys' not in item:
                            middlehand[item['key']] = item['key']
                            continue
                        middlehand[item['key']] = item['subkeys']
                    else:
                        middlehand[item] = item
                data[s] = middlehand
            else:
                data[s] = set(input_data[s])

    data.is_environment = lambda query: query in data.environments
    data.is_subkey = lambda env_name, query: data.is_environment(env_name) and query in data.environments[env_name]
    data.is_key = lambda query: query in data.keys
    data.is_alias = lambda query: query in data.aliases

    return data


def load(file, config: DotDict) -> DotDict:
    """
    Parses a qml formatted file according to the configuration supplied.

    Parameters
    ----------
    file : TextIOWrapper
        A file stream to read the qml file from.
    config : DotDict
        A configuration loaded using `load_config` to supply information about what to load.

    Returns
    -------
    DotDict
        A dictionary containing the data parsed according to qml formatting.

    """
    loader = Loader(file, config)
    return loader.load()
