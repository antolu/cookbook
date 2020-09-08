#!/usr/bin/env python

import sys

sys.path.insert(0, './django/')

import logging
from os import path, environ
import pprint
from argparse import ArgumentParser

environ.setdefault("DJANGO_SETTINGS_MODULE", "webapps.settings")
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

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

    io = {'root_dir': root_dir, 'basename': basename, 'in_file': in_file, 'img_dir': args.image_dir,
          'output_dir': args.output_dir}

    with open(args.recipe, 'r') as f:
        recipe_data = parse_file(f)

    file_for_output = recipe_data.to_qml()

    log.info(pprint.pformat(file_for_output))

    with open('sources/test.txt', 'w') as f:
        dump(file_for_output, f)

    return

    # print('-'*90)
    # print('JSONd data')

    # output = format_for_output(recipe_data)
    # pp.pprint(output)

    # get_img(recipe_data, io)

    out_filename = path.join(io['output_dir'], '{}.tex'.format(io['basename']))

    write_recipe(recipe_data.to_qml(), out_filename)

    if args.source_only:
        sys.exit(0)

    # run latexmk
    compile(path.splitext(out_filename)[0])


def get_args():
    parser = ArgumentParser()

    parser.add_argument(
        "recipe", help="The basename of the recipe (without .yml file extension", type=str)
    parser.add_argument('-l', '--language', help='The language of the output recipe',
                        default='all', type=str, choices=('en', 'sv'))
    parser.add_argument(
        '-d', '--debug', help='Enable debug logging', action='store_true')
    parser.add_argument('-s', '--source-only', help='Only generate latex sourcefile',
                        action='store_true', dest='source_only')
    parser.add_argument(
        '--output-dir', help='The directory to output .tex and .pdf files', type=str, dest='output_dir',
        default='output')
    parser.add_argument(
        '--image-dir', help='The directory that contains the images', type=str, dest='image_dir', default='images')
    parser.add_argument(
        '--source-dir', help='The directory that contains the source files', dest='source_dir', default='sources')

    parser.add_argument(
        '--hide-notes', help='Do not include notes in final output', action='store_true', dest='hide_notes')
    parser.add_argument('--hide-changelog',
                        help='Do not include changelog in final output', action='store_true', dest='hide_changelog')

    args = parser.parse_args()

    return args


if __name__ == '__main__':
    main()
