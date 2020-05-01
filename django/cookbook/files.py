from os import path
from yaml import load, FullLoader

from .models import Recipe
from .parsers import parse_file, dict_to_json


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

    recipe = Recipe(**output)

    recipe.save()
