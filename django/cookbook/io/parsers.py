import logging
from pprint import pformat

from cookbook.io.recipefile import RecipeFile
from qml import load, load_config

log = logging.getLogger(__name__)


def parse_file(f, config: str = 'parser_config.yml') -> RecipeFile:
    with open(config, 'r') as c:
        parser_config = load_config(c)

    data = load(f, config=parser_config)

    log.info(pformat(data))

    return RecipeFile(data, format='io')
