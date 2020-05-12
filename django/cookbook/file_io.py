import logging
from glob import glob
from os import path, mkdir, remove
from os import system as shell
from sys import exit

from shutil import which

log = logging.getLogger('log')
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


def write_recipes(data: dict, io: dict, options: dict):
    files_written = list()

    for language, language_data in data.items():
        out_filename = path.join(io['output_dir'],
                                 '{}.{}.tex'.format(io['basename'], language))

        with open(out_filename, 'w') as f:
            write = get_writer(f)
            log.info("Writing file {}".format(out_filename))

            write('\\documentclass[a4paper, 11pt]{article}\n')
            write('\\usepackage{cookbook}\n')

            write('\\title{{{}}}\n'.format(language_data['name']))

            if 'yields' in language_data and language_data['yields'] is not None:
                write('\\yields{{ {} }}\n'.format(language_data['yields']))
            else:
                log.info('Field yield does not exist.')

            if 'description' in language_data and language_data['description']:
                write('\\description{{ {} }}\n'.format(language_data['description']))
            else:
                log.info('Field description does not exist.')

            if 'temperature' in language_data and language_data['temperature']:
                write('\\temperature{{ {} }}\n'.format(language_data['temperature']))
            else:
                log.info('Field temperature does not exist.')

            if 'cookingtime' in language_data and language_data['cookingtime']:
                write('\\cookingtime{{ {} }}\n'.format(language_data['cookingtime']))
            else:
                log.info('Field cookingtime does not exist.')

            if language_data['img'] is not None:
                write('\\image{{ {} }}'.format(language_data['img']))

            if language_data['has_changelog'] and language_data['changelog']:
                write('\\date{{ {} }}'.format(language_data['changelog'][0]['date']))

            write('\\providecommand\\ingredients{%')
            for ingredient_part in language_data['ingredients']:
                write_ingredients(ingredient_part, f)
            write('}')

            write()

            write('\\providecommand\\instructions{%')
            for step_part in language_data['steps']:
                write_steps(step_part, f)
            write('}')

            write()

            if language_data['has_notes'] and not options['hide_notes']:
                write('\\providecommand\\notes{%')
                with Environment(f, 'compactlist') as e:
                    for note in language_data['note']:
                        write('\t\\noteitem {}'.format(note))
                write('}')

            if language_data['has_changelog'] and not options['hide_changelog']:
                write('\\providecommand\\changelog{%')
                with Environment(f, 'changelog') as e:
                    for change in language_data['changelog']:
                        entry = '{}\n'.format(change['date'])
                        if not isinstance(change['change'], list):
                            entry += change['change']
                        else:
                            for line in change['change']:
                                entry += '\t{}\n'.format(line)
                        write('\t\\noteitem {}'.format(entry))
                write('}')

            files_written.append(out_filename)

    log.info('Written files {}'.format(' '.join(files_written)))

    return files_written


def write_ingredients(ingredients, f):
    write = get_writer(f)

    if ingredients['name'] or ingredients['name']:
        write('\\ingredientpart{{ {} }}'.format(ingredients['name']))

    with Environment(f, 'compactlist') as e:
        for ingredient in ingredients['list']:
            write('\t\\ingredient {}'.format(ingredient))


def write_steps(steps: dict, f):
    write = get_writer(f)

    if steps['name'] or steps['name']:
        write('\\steppart{{ {} }}'.format(steps['name']))

    with Environment(f, 'steps') as e:
        for step in steps['list']:
            write('\t\\step {}'.format(step))


def compile(files: list):
    """
    Run pdflatex

    param : files The files to run pdflatex on

    """
    if which('pdflatex') is None:
        log.error('pdflatex could not be found. Leaving Latex source files as-is.')
        exit(2)
    else:
        for f in files:
            output_dir = path.split(f)[0]
            command = r'latexmk -xelatex -output-directory={} {}'.format(
                output_dir.replace(' ', '\\ '), f.replace(' ', '\\ '))
            log.info('Running command {}'.format(command))
            shell(command)

        log.info('PDF files successfully generated. ')
        log.info('Cleaning up')

        to_delete = list()
        for f in files:
            basename = path.splitext(path.basename(f))[0]
            to_delete.append(path.join(output_dir, '{}.log'.format(basename)))
            to_delete.append(path.join(output_dir, '{}.aux'.format(basename)))

        for f in to_delete:
            log.debug('Deleting file {}'.format(path.basename(f)))
            remove(f)
