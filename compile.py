#!/usr/bin/env python

import sys
sys.path.insert(0, 'django/cookbook')
import logging
from os import path
import pprint

from util import get_args
from parsers import parse_file, dict_to_json
from file_io import compile, write_recipes, get_img, make_output_dir

log = logging.getLogger('log')
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
    options = {'hide_notes' : args.hide_notes, 'hide_changelog' : args.hide_changelog, 'source_only' : args.source_only}
    data = dict()

    with open(in_file, 'r') as f:
        recipe_data = parse_file(f, {'language': args.language})
        # data = load(f, Loader=FullLoader)

    pp.pprint(recipe_data)

    print('-'*90)
    print('JSONd data')

    output = dict_to_json(recipe_data)
    pp.pprint(output)
    # recipe_data = parse_recipes(args, data)

    # return 0

    get_img(recipe_data, io)

    make_output_dir(io)

    files_written = write_recipes(recipe_data, io, options)

    if args.source_only:
        sys.exit(0)

    # run pdflatex
    compile(files_written)


if __name__ == '__main__':
    main()
