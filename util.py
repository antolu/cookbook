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


