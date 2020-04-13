#!/usr/bin/env python

import sys
import logging
from os import path

from argparse import ArgumentParser
from yaml import load, FullLoader

from parsers import get_args, parse_recipes
from file_io import get_writer, get_img, Environment, write_ingredients, write_steps, make_output_dir, write_recipes, compile

log = logging.getLogger('log')
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
log.addHandler(ch)

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
        data = load(f, Loader=FullLoader)

    recipe_data = parse_recipes(args, data)
    get_img(recipe_data, io)

    make_output_dir(io)

    files_written = write_recipes(recipe_data, io, options)

    if args.source_only:
        sys.exit(0)

    # run pdflatex
    compile(files_written, io)

if __name__ == '__main__':
    main()