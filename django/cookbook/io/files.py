from os import path

from cookbook.models import Recipe
from qml import load_config, load
import logging

from pprint import pformat
from io import TextIOWrapper

from .recipefile import RecipeFile

log = logging.getLogger(__name__)


def handle_uploaded_file(f):
    if not f.size < 1e6:
        raise MemoryError('File too big!')

    filename = f.name
    ext = path.splitext(filename)[-1]
    if ext not in ('.rcp', '.txt'):
        raise NameError('File extension \'{}\' is invalid.'.format(ext))

    # TODO: also check if file is raw text or binary

    file = TextIOWrapper(f.file)
    recipe_file = parse_file(file)

    output = recipe_file.to_djangodb()

    # If recipe with same UUID exists, try to update it, else create a new one.
    if 'uuid' in output and output['uuid']:
        try:
            current_version = Recipe.objects.get(pk=output['uuid'])
            log.info('Replacing currently existing recipe with new one.')

            for field in current_version.__dict__:
                if field in output:
                    current_version.__dict__[field] = output[field]

            current_version.save()
            return

        except Recipe.DoesNotExist:
            pass

    log.info('Creating new recipe entry for {}'.format(output['name']))

    recipe = Recipe(**output)

    recipe.save()


def parse_file(f, config: str = 'config/parser_config.yml') -> RecipeFile:
    with open(config, 'r') as c:
        parser_config = load_config(c)

    data = load(f, config=parser_config)

    return RecipeFile(data, format='io')
