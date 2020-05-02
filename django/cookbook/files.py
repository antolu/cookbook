from os import path
from yaml import load, FullLoader

from .models import Recipe
from .parsers import parse_file, dict_to_json

import logging
log = logging.getLogger(__name__)
from pprint import pformat


def handle_uploaded_file(f):
    if not f.size < 1e6:
        raise MemoryError('File too big!')

    # f.read()
    filename = f.name
    ext = path.splitext(filename)[-1]
    if ext not in ('.yml', '.yaml', '.txt'):
        raise NameError('File extension \'{}\' is invalid.'.format(ext))

    parsed_file = parse_file(f)
    output = dict_to_json(parsed_file)

    log.info(pformat(output))

    if 'uuid' in output and output['uuid']:
        try:
            current_version = Recipe.objects.get(pk=output['uuid'])
            log.info('Replacing currently existing recipe with new one.')

            for field in current_version.__dict__:
                if field in output:
                    current_version.__dict__[field] = output[field]

            current_version.save()

        except Recipe.DoesNotExist:
            log.info('Creating new recipe entry for {}'.format(output['title']))
            recipe = Recipe(**output)

            recipe.save()
