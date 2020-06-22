#!/usr/bin/env python

import sys
# sys.path.insert(0, 'django/cookbook')
sys.path.insert(0, './django/')
# sys.path.append('django')
import logging
from os import path, environ
import pprint

environ.setdefault("DJANGO_SETTINGS_MODULE", "webapps.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from util import get_args
from cookbook.io.files import parse_file
from cookbook.io.latex import write_recipe
from cookbook.io.recipefile import RecipeFile
from qml import dump


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
log.addHandler(ch)

pp = pprint.PrettyPrinter(indent=4)


def main():

    args = get_args()
    log.debug('passed arguments: {}'.format(args))

    root_dir = path.split(path.abspath(__file__))[0]

    basename = args.recipe
    in_file = path.join(root_dir, args.source_dir, basename + '.yml')

    io = {'root_dir' : root_dir, 'basename' : basename, 'in_file' : in_file, 'img_dir' : args.image_dir, 'output_dir' : args.output_dir}

    with open(args.recipe, 'r') as f:
        recipe_data = parse_file(f)

    file_for_output = recipe_data.format_io()

    log.info(pprint.pformat(file_for_output))

    with open('test.txt', 'w') as f:
        dump(file_for_output, f)

    exit(0)

    # print('-'*90)
    # print('JSONd data')

    # output = format_for_output(recipe_data)
    # pp.pprint(output)

    # get_img(recipe_data, io)

    out_filename = path.join(io['output_dir'], '{}.tex'.format(io['basename']))

    write_recipe(recipe_data.format_io(), out_filename)

    if args.source_only:
        sys.exit(0)

    # run latexmk
    compile(path.splitext(out_filename)[0])


if __name__ == '__main__':
    main()
