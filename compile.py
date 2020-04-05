#!/usr/bin/env python

from argparse import ArgumentParser
from yaml import load, FullLoader
import os
import sys
import pprint
import logging
from parsers import get_args, parse_recipes
from file_io import get_writer, Environment, write_ingredients, write_steps
from os import path
from glob import glob
from shutil import which
from os import system as shell

pp = pprint.PrettyPrinter()
log = logging.getLogger('log')
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
log.addHandler(ch)

log.info('something')

args = get_args()

root_dir = os.path.split(os.path.abspath(__file__))[0]

basename = args.recipe
in_file = path.join(root_dir, args.source_dir, basename + '.yml')

img_dir = path.join(root_dir, args.image_dir)
img = None
if not path.exists(img_dir):
    log.info('Folder {} does not exist. No image will be used.'.format(img_dir))
else:
    potential_imgs = glob(
        path.join(root_dir, img_dir, '{}.*'.format(basename)))
    if len(potential_imgs) == 0:
        log.warning('No image files could be found')
    else:
        img = potential_imgs[0]

with open(in_file, 'r') as f:
    data = load(f, Loader=FullLoader)

log.debug('passed arguments: {}'.format(args))

recipe_data = parse_recipes(args, data)

files_written = list()

output_dir = path.join(root_dir, args.output_dir)
if not path.exists(output_dir):
    log.info('Output directory does not exist. Creating it. ')
    os.mkdir(output_dir)

for language, data in recipe_data.items():
    out_filename = path.join(root_dir, args.output_dir,
                             '{}.{}.tex'.format(basename, language))

    with open(out_filename, 'w') as f:
        write = get_writer(f)

        write('\\documentclass[a4paper, 11pt]{article}\n')
        write('\\usepackage{cookbook}\n')

        if 'name' in data and data['name'] is not None:
            write('\\title{{{}}}\n'.format(data['name']))

        if 'yields' in data and data['yields'] is not None:
            write('\\yields{{ {} }}\n'.format(data['yields']))
        else:
            log.info('field yield does not exist')

        if img is not None:
            write('\\image{{{}}}'.format(img))

        if data['has_changelog']:
            write('\\date{{{}}}'.format(data['changelog'][0]['date']))

        with Environment(f, 'document') as e:

            write('\\maketitle')

            write('\\subsection*{Ingredients}\n')

            for ingredient_part in data['ingredients']:
                write_ingredients(ingredient_part, f)

            write()

            write('\\subsection*{Instructions}\n')
            for step_part in data['steps']:
                write_steps(step_part, f)

            write()

            if data['has_notes'] and not args.hide_notes:
                write('\\section{Notes and tips}\n')
                with Environment(f, 'itemize') as e:
                    for note in data['note']:
                        write('\t\\noteitem {}'.format(note))

            if data['has_changelog'] and not args.hide_changelog:
                write('\\appendix{Changelog}')
                with Environment(f, 'changelog') as e:
                    for change in data['changelog']:
                        entry = '{}\n'.format(change['date'])
                        if not isinstance(change['change'], list):
                            entry += change['change']
                        else:
                            for line in change['change']:
                                entry += '\t{}\n'.format(line)
                        write('\t\\noteitem {}'.format(entry))

        write('\\end{document}')

        files_written.append(out_filename)

log.info('Written files {}'.format(' '.join(files_written)))
if args.source_only:
    sys.exit(0)

# run pdflatex
if which('pdflatex') is None:
    log.error('pdflatex could not be found. Leaving Latex source files as-is.')
    sys.exit(2)
else:
    for f in files_written:
        # shell('pdflatex \'{}\''.format(f.replace(' ', '\\ ')))
        command = 'pdflatex \'{}\' -output-directory={}'.format(
            f, path.join(root_dir, args.output_dir))
        log.info('Running command {}'.format(command))
        shell(command)

    log.info('PDF files successfully generated. ')
    log.info('Cleaning up')

    to_delete = list()
    for f in files_written:
        basename = path.splitext(path.basename(f))[0]
        to_delete.append(path.join(root_dir, output_dir, '{}.log'))
        to_delete.append(path.join(root_dir, output_dir, '{}.aux'))

    for f in to_delete:
        log.debug('Deleting file {}'.format(path.basename(f)))
