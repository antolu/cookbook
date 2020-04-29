from os import path
from yaml import load, FullLoader

from .models import Recipe
from .parsers import parse_file, dict_to_json


def handle_uploaded_file(f):
    if not f.size < 1e6:
        print('This should throw an exception.')

    # f.read()
    filename = f.name
    if path.splitext(filename)[1] not in ('yml', 'yaml', 'txt'):
        print('This should also throw an exception.')

    parsed_file = parse_file(f, {'language': 'all'})

    output = dict_to_json(parsed_file)

    recipe = Recipe(**output)

    recipe.save()
