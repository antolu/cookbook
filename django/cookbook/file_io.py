import logging
from glob import glob
from os import path, mkdir, remove
from os import popen as shell
from sys import exit

from django.template import loader
from django.shortcuts import render

from shutil import which

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


# TODO: add key override for parsing, eg top level 'temperature' van be overriden by language specific 'temperature'
# TODO: add logging for everything
# TODO: modularise script
# TODO: add option to remove .tex files
# TODO: override with immediate filename instead of shortname without extension (basename.extension instead of basename)
# TODO: allow compiling several recipes at once into a single PDF, or separate (selectable)
# TODO: add GUI
# TODO: add option to compile all available recipes in a directory


class Environment:
    def __init__(self, f, env):
        self.f = f
        self.env = env

    def __enter__(self):
        self.f.write('\\begin{{{}}}\n'.format(self.env))

    def __exit__(self, exc_type, exc_value, tb):
        self.f.write('\\end{{{}}}\n'.format(self.env))


def get_writer(f):
    return lambda s='', end='\n': print(s, file=f, end=end)


def get_img(data: dict, io: dict):
    img_dir = path.join(io['root_dir'], io['img_dir'])
    img = None
    if not path.exists(io['img_dir']):
        log.info('Folder {} does not exist. No image will be used.'.format(img_dir))
    else:
        potential_imgs = glob(
            path.join(img_dir, '{}.*'.format(io['basename'])))
        if len(potential_imgs) > 1:
            log.warning('More than one images found. Choosing the first by default.')
        if len(potential_imgs) == 0:
            log.warning('No image files could be found')
        else:
            img = potential_imgs[0]

    for lang, data in data.items():
        data['img'] = img


def make_output_dir(io: dict):
    io['output_dir'] = path.join(io['root_dir'], io['output_dir'])
    if not path.exists(io['output_dir']):
        log.info('Output directory does not exist. Creating it. ')
        mkdir(io['output_dir'])


def write_recipe(data: dict, filename: str = None, raw_buffer=False):
    t = loader.get_template('cookbook/recipe_template.tex')

    buffer = t.render({'recipe': data})
    if raw_buffer:
        log.info('Returning raw buffer')
        return buffer

    if not filename:
        raise RuntimeError('Filename not specified.')

    with open(filename, 'w') as f:
        f.write(buffer)

    log.info('Written file {}'.format(filename))


def write_ingredients(ingredients, f) -> None:
    write = get_writer(f)

    if ingredients['name'] or ingredients['name']:
        write('\\ingredientpart{{ {} }}'.format(ingredients['name']))

    with Environment(f, 'compactlist') as e:
        for ingredient in ingredients['list']:
            write('\t\\ingredient {}'.format(ingredient))


def write_steps(steps: dict, f) -> None:
    write = get_writer(f)

    if steps['name'] or steps['name']:
        write('\\steppart{{ {} }}'.format(steps['name']))

    with Environment(f, 'steps') as e:
        for step in steps['list']:
            write('\t\\step {}'.format(step))


def compile(file: str) -> None:
    """
    Run pdflatex

    param : files The files to run pdflatex on

    """
    if which('latexmk') is None or which('xelatex') is None:
        log.error('xelatex or latexmk could not be found. Leaving Latex source files as-is.')
        exit(2)
    else:
        output_dir = path.split(file)[0]
        command = r'latexmk -xelatex -output-directory={} {}'.format(
            output_dir.replace(' ', '\\ '), file.replace(' ', '\\ '))
        log.info('Running command {}'.format(command))
        code = shell(command).read()
        if code != '0':
            log.error('latexmk failed. Check the log file for errors')
            return

        log.info('PDF files successfully generated. ')
        log.info('Cleaning up')

        to_delete = list()
        basename = path.splitext(path.basename(file))[0]
        to_delete.append(path.join(output_dir, '{}.log'.format(basename)))
        to_delete.append(path.join(output_dir, '{}.aux'.format(basename)))

        for file in to_delete:
            log.debug('Deleting file {}'.format(path.basename(file)))
            remove(file)
