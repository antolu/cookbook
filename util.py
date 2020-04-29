from argparse import ArgumentParser
import logging
import sys

log = logging.getLogger('log')


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
        '--output-dir', help='The directory to output .tex and .pdf files', type=str, dest='output_dir', default='output')
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


def parse_recipes(args, data):
    if 'recipe' not in data:
        log.error('Could not find key \'recipe\' in the file.')
        sys.exit(1)

    recipe_data = data['recipe']
    orig_data = data

    recipes = dict()

    # parse languages
    if args.language != 'all':
        for item in recipe_data:
            if item['language'] == args.language:
                break
            else:
                continue

            # finally
            log.error('Recipe written in {} not found'.format(args.language))
            sys.exit(1)

        recipes[args.language] = dict()
    else:
        for item in recipe_data:
            recipes[item['language']] = dict()

    # check if recipe is divided into steps
    for item in recipe_data:
        language = item['language']
        data = recipes[language]

        if 'yields' in item:
            data['yields'] = item['yields']
        if not 'name' in item:
            log.warning('Recipe has no name.')
        else:
            data['name'] = item['name']
        if 'parts' in item:
            data['has_parts'] = True
            data['ingredients'] = list()
            data['steps'] = list()
            data['notes'] = list()

            for part in item['parts']:
                ingredients = list()
                steps = list()
                notes = list()

                for ingredient in part['ingredients']:
                    ingredients.append(ingredient)
                for step in part['steps']:
                    steps.append(step)

                is_optional = False
                if 'optional' in part and part['optional']:
                    is_optional = True

                data['ingredients'].append(
                    {'list': ingredients, 'optional': is_optional, 'name': part['name'] if 'name' in part else None})
                data['steps'].append(
                    {'list': steps, 'optional': is_optional, 'name': part['name'] if 'name' in part else None})

            if 'notes' in item:  # notes exist for this language
                data['has_notes'] = True
                for note in item['notes']:
                    data['notes'].append(note)

            else:
                data['has_notes'] = False
                log.debug('{} notes parsed for language {}'.format(
                    len(data['notes']), language))

        else:  # only no parts in recipe
            data['has_parts'] = False
            data['ingredients'] = list()
            data['steps'] = list()

            for ingredient in recipe_data['ingredients']:
                data['ingredients'].append(ingredient)
            for step in recipe_data['steps']:
                data['steps'].append(step)

            if 'notes' in recipe_data:  # notes exist
                data['notes'] = list()
                data['has_notes'] = True
                for note in recipe_data:
                    data['notes'].append(note)
            else:
                data['has_notes'] = False

        if 'changelog' in orig_data:  # changelog exists
            data['has_changelog'] = True

            data['changelog'] = list()
            for entry in orig_data['changelog']:
                data['changelog'].append(entry)

        else:
            data['has_changelog'] = False

    return recipes
