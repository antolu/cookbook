#!/usr/bin/env python

import sys
sys.path.insert(0, 'django/cookbook')
sys.path.append('django')
import logging
from os import path, environ
import pprint

from util import get_args
from parsers import parse_file, dict_to_json, format_for_output
from file_io import compile, write_recipe, get_img, make_output_dir
environ.setdefault("DJANGO_SETTINGS_MODULE", "webapps.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()


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

    with open(in_file, 'r') as f:
        recipe_data = parse_file(f)

    # pp.pprint(recipe_data)

    # print('-'*90)
    # print('JSONd data')

    # output = format_for_output(recipe_data)
    # pp.pprint(output)

    # get_img(recipe_data, io)

    make_output_dir(io)

    out_filename = path.join(io['output_dir'], '{}.tex'.format(io['basename']))

    write_recipe(recipe_data, out_filename)

    if args.source_only:
        sys.exit(0)

    # run latexmk
    compile(path.splitext(out_filename)[0])


if __name__ == '__main__':
    main()
