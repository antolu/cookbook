import logging
from glob import glob
from os import path, mkdir, remove
from os import popen as shell
import inspect
from sys import exit

from django.template import loader
from django.shortcuts import render

from shutil import which

from .. import ROOT_DIR

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Environment:
    """
    Helper class to write a latex verbatim environment.

    Used as
    ```
    with Environment(file_stream, verbatim_name) as e:
        write_line(some_string)
    ```
    """
    def __init__(self, f, env):
        self.f = f
        self.env = env

    def __enter__(self):
        self.f.write('\\begin{{{}}}\n'.format(self.env))

    def __exit__(self, exc_type, exc_value, tb):
        self.f.write('\\end{{{}}}\n'.format(self.env))


def get_writer(f):
    """
    Get a function handle to write strings to a stream without having to explicitly write newline at the end.

    Parameters
    ----------
    f : TextIO
        File stream to create a wrapper for.

    Returns
    -------
    function
        A lambda function taking arguments s: str, end: str. Writes string `s`, and ends the write with `end`.
    """
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
    Compile a file using latexmk and xelatex. The output PDF file is placed in the same directory
    as the source file.

    Also removes auxiliary files produced by the latex compiler when finished.

    Parameters
    ----------
    file : str
        The path to the file to compile

    Raises
    ------
    RuntimeError:
        If xelatex or latexmk cannot be count.
    """
    if which('latexmk') is None or which('xelatex') is None:
        raise RuntimeError('xelatex or latexmk could not be found. Leaving Latex source files as-is.')

    output_dir = path.split(file)[0]
    command = r'TEXINPUTS={}//:$TEXINPUTS latexmk -xelatex -output-directory={} {}'.format(
        ROOT_DIR, output_dir.replace(' ', '\\ '), file.replace(' ', '\\ '))
    log.info('Running shell command {}'.format(command))
    code = shell(command).read()
    if code != '0':
        log.error('latexmk failed. Check the log file for errors')
    else:
        log.info('PDF file successfully generated. ')

    log.info('Cleaning up')

    # Delete remaining files
    to_delete = list()
    basename = path.splitext(path.basename(file))[0]
    to_delete.append(path.join(output_dir, '{}.log'.format(basename)))
    to_delete.append(path.join(output_dir, '{}.aux'.format(basename)))

    for file in to_delete:
        log.debug('Deleting file {}'.format(path.basename(file)))
        remove(file)
